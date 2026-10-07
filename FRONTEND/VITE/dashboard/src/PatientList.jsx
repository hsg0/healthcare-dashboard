// WHAT — The patient screens: the searchable list and the single-patient page.
// WHY — These are the screens that show real records from the FastAPI service.
// HOW — App.jsx routes "/patients" here and "/patients/:patientId" to the detail view. Both read the API with fetch.
// IMPORTANT — Always show loading, empty, not-found, and network-error states. Never show success when the request failed. The API decides what is valid; these controls only offer the choices the API accepts.

import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

// Point this at a different API with VITE_API_BASE_URL when the app is not running locally.
export const apiBaseAddress = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:4020"

const statusChoices = [
  { value: "", label: "All statuses" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "critical", label: "Critical" },
]

const sortChoices = [
  { value: "last_name", label: "Last name" },
  { value: "first_name", label: "First name" },
  { value: "age", label: "Age" },
  { value: "last_visit", label: "Last visit" },
  { value: "status", label: "Status" },
]

const patientsPerPage = 10

export function PatientList() {
  const [searchText, setSearchText] = useState("")
  const [selectedStatus, setSelectedStatus] = useState("")
  const [sortBy, setSortBy] = useState("last_name")
  const [sortDirection, setSortDirection] = useState("asc")
  const [currentPage, setCurrentPage] = useState(1)

  const [patients, setPatients] = useState([])
  const [totalCount, setTotalCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [loadErrorMessage, setLoadErrorMessage] = useState("")

  // Go back to page one whenever the question changes, so we never ask for a page that no longer exists.
  useEffect(() => {
    setCurrentPage(1)
  }, [searchText, selectedStatus, sortBy, sortDirection])

  useEffect(() => {
    const requestCancel = new AbortController()
    // Wait a moment so typing a name does not send one request per keystroke.
    const typingPause = setTimeout(async () => {
      setIsLoading(true)
      setLoadErrorMessage("")

      const searchParameters = new URLSearchParams({
        page: String(currentPage),
        page_size: String(patientsPerPage),
        sort_by: sortBy,
        sort_dir: sortDirection,
      })
      if (searchText.trim()) searchParameters.set("search", searchText.trim())
      if (selectedStatus) searchParameters.set("status", selectedStatus)

      try {
        const response = await fetch(`${apiBaseAddress}/patients?${searchParameters}`, {
          signal: requestCancel.signal,
        })
        if (!response.ok) {
          throw new Error(`The server answered with status ${response.status}.`)
        }
        const page = await response.json()
        setPatients(page.patients)
        setTotalCount(page.total_count)
      } catch (error) {
        if (error.name === "AbortError") return
        setPatients([])
        setTotalCount(0)
        setLoadErrorMessage("The patient list could not be loaded. Check that the API is running, then try again.")
      } finally {
        if (!requestCancel.signal.aborted) setIsLoading(false)
      }
    }, 300)

    return () => {
      clearTimeout(typingPause)
      requestCancel.abort()
    }
  }, [searchText, selectedStatus, sortBy, sortDirection, currentPage])

  const lastPage = Math.max(1, Math.ceil(totalCount / patientsPerPage))

  return (
    <section className="patient-page">
      <div className="title-row">
        <div>
          <h1>Patients</h1>
          <p>Search, filter, and open a patient record.</p>
        </div>
        {/* A count would be a lie while the request is failing or still running. */}
        {!isLoading && !loadErrorMessage && <span className="week-pill">{totalCount} total</span>}
      </div>

      <div className="card patient-controls">
        <label>
          <span>Search by name</span>
          <input
            type="search"
            value={searchText}
            placeholder="First or last name"
            onChange={(event) => setSearchText(event.target.value)}
          />
        </label>

        <label>
          <span>Status</span>
          <select value={selectedStatus} onChange={(event) => setSelectedStatus(event.target.value)}>
            {statusChoices.map((choice) => (
              <option key={choice.label} value={choice.value}>{choice.label}</option>
            ))}
          </select>
        </label>

        <label>
          <span>Sort by</span>
          <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            {sortChoices.map((choice) => (
              <option key={choice.value} value={choice.value}>{choice.label}</option>
            ))}
          </select>
        </label>

        <label>
          <span>Order</span>
          <select value={sortDirection} onChange={(event) => setSortDirection(event.target.value)}>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </label>
      </div>

      {isLoading && <p className="message-panel">Loading patients…</p>}

      {!isLoading && loadErrorMessage && (
        <p className="message-panel message-error" role="alert">{loadErrorMessage}</p>
      )}

      {!isLoading && !loadErrorMessage && patients.length === 0 && (
        <p className="message-panel">No patient matches this search.</p>
      )}

      {!isLoading && !loadErrorMessage && patients.length > 0 && (
        <>
          <article className="card">
            <table className="patient-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Status</th>
                  <th>Last visit</th>
                  <th>City</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>{patient.first_name} {patient.last_name}</td>
                    <td>{patient.patient_age}</td>
                    <td><em className={`status-pill status-${patient.status}`}>{patient.status}</em></td>
                    <td>{patient.last_visit}</td>
                    <td>{patient.city}</td>
                    <td><Link className="text-button" to={`/patients/${patient.id}`}>View</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <div className="page-controls">
            <button
              type="button"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage <= 1}
            >
              Previous
            </button>
            <span>Page {currentPage} of {lastPage}</span>
            <button
              type="button"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= lastPage}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  )
}

export function PatientDetail() {
  const { patientId } = useParams()

  const [patient, setPatient] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [loadErrorMessage, setLoadErrorMessage] = useState("")

  useEffect(() => {
    const requestCancel = new AbortController()

    async function loadOnePatient() {
      setIsLoading(true)
      setLoadErrorMessage("")
      setPatient(null)

      try {
        const response = await fetch(`${apiBaseAddress}/patients/${patientId}`, {
          signal: requestCancel.signal,
        })
        if (response.status === 404 || response.status === 422) {
          setLoadErrorMessage(`No patient has the id "${patientId}".`)
          return
        }
        if (!response.ok) {
          throw new Error(`The server answered with status ${response.status}.`)
        }
        setPatient(await response.json())
      } catch (error) {
        if (error.name === "AbortError") return
        setLoadErrorMessage("This patient could not be loaded. Check that the API is running, then try again.")
      } finally {
        if (!requestCancel.signal.aborted) setIsLoading(false)
      }
    }

    loadOnePatient()
    return () => requestCancel.abort()
  }, [patientId])

  if (isLoading) {
    return <p className="message-panel">Loading this patient…</p>
  }

  if (loadErrorMessage) {
    return (
      <section className="message-panel message-error" role="alert">
        <h1>Patient not available</h1>
        <p>{loadErrorMessage}</p>
        <Link className="text-button" to="/patients">Back to all patients</Link>
      </section>
    )
  }

  const patientFacts = [
    { label: "Date of birth", value: patient.date_of_birth },
    { label: "Age", value: `${patient.patient_age} years` },
    { label: "Blood type", value: patient.blood_type },
    { label: "Last visit", value: patient.last_visit },
    { label: "Email", value: patient.email },
    { label: "Phone", value: patient.phone },
    { label: "Address", value: `${patient.address_line}, ${patient.city}, ${patient.state} ${patient.postal_code}` },
    { label: "Allergies", value: patient.allergies || "None recorded" },
    { label: "Conditions", value: patient.conditions || "None recorded" },
  ]

  return (
    <section className="patient-page">
      <div className="title-row">
        <div>
          <h1>{patient.first_name} {patient.last_name}</h1>
          <p>Patient record #{patient.id}</p>
        </div>
        <em className={`status-pill status-${patient.status}`}>{patient.status}</em>
      </div>

      <article className="card">
        <dl className="patient-facts">
          {patientFacts.map((fact) => (
            <div key={fact.label}>
              <dt>{fact.label}</dt>
              <dd>{fact.value}</dd>
            </div>
          ))}
        </dl>
      </article>

      <p><Link className="text-button" to="/patients">Back to all patients</Link></p>
    </section>
  )
}
