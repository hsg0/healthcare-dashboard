// WHAT — The healthcare dashboard screen.
// WHY — This is the home page people see at http://localhost:5173/.
// HOW — It lays out the nursing cards, then the revenue-cycle cards. The numbers are sample data in this file.
// IMPORTANT — These numbers are not from the API yet. The assistant box does not answer medical questions.

const doctors = [
  { name: "Dr. Olivia Bennett", specialty: "Cardiologist", status: "On Duty" },
  { name: "Dr. Marcus Lee", specialty: "Orthopedic Surgeon", status: "Available" },
  { name: "Dr. Samuel Ortiz", specialty: "Orthopedic Surgeon", status: "On Duty" },
  { name: "Dr. Milang Carter", specialty: "Pediatrician", status: "On Leave" },
  { name: "Dr. Marco Singh", specialty: "Dermatologist", status: "Available" },
]

const appointments = [
  { time: "09:20", patientName: "Michael Chen", visitType: "Follow-up Consultation" },
  { time: "10:20", patientName: "Michael Chen", visitType: "Follow-up Consultation" },
  { time: "12:20", patientName: "Michael Chen", visitType: "Follow-up Consultation" },
  { time: "2:20", patientName: "Michael Chen", visitType: "Follow-up Consultation" },
  { time: "3:20", patientName: "Michael Chen", visitType: "Follow-up Consultation" },
]

const careStats = [
  { label: "Total Patients", value: "128", progress: 70 },
  { label: "Stable Patients", value: "86 / 128", progress: 67 },
  { label: "Critical Patients", value: "12 / 128", progress: 18 },
  { label: "Discharges Patients", value: "24 / 128", progress: 30 },
]

const revenueMetrics = [
  { label: "Denial Rates", value: "3.1%", change: "-0.4% vs last month", target: "Target: 2.5%", tone: "warning", fill: 62 },
  { label: "AR Days", value: "38 Days", change: "4.5d vs last quarter", target: "Target: 35 Days", tone: "critical", fill: 78 },
  { label: "Clean Claim Rate", value: "96.5%", change: "+1.1% vs yesterday", target: "Target: 98%", tone: "warning", fill: 96 },
  { label: "Overall Revenue Performance", value: "$1.2M", change: "+5% vs last week", target: "Target: $1.1M", tone: "good", fill: 88 },
]

const denialReasons = [
  { label: "Duplicate Claim", percent: 22 },
  { label: "Claim Incomplete", percent: 19 },
  { label: "Incorrect Payer", percent: 17 },
  { label: "Payer Rule", percent: 14 },
  { label: "Timely Filing", percent: 11 },
]

const agingBuckets = [
  { label: "0-30 Days", current: 72, target: 55 },
  { label: "31-60 Days", current: 48, target: 36 },
  { label: "61-90 Days", current: 30, target: 22 },
  { label: ">90 Days", current: 18, target: 12 },
]

const claimMilestones = [
  { name: "Claim Created", date: "12/01", state: "Complete" },
  { name: "Clean Claim Check", date: "12/02", state: "Pending Check" },
  { name: "Claim Submitted", date: "12/03", state: "Complete" },
  { name: "Payer Response", date: "12/10", state: "Planned" },
  { name: "Denial Handling", date: "12/12", state: "Scheduled" },
]

function HalfGauge({ fill, value }) {
  return (
    <svg className="half-gauge" viewBox="0 0 100 58" aria-hidden="true">
      <path d="M10 50 A 40 40 0 0 1 90 50" pathLength="100" />
      <path
        className="half-gauge-fill"
        d="M10 50 A 40 40 0 0 1 90 50"
        pathLength="100"
        strokeDasharray={`${fill} 100`}
      />
      <text x="50" y="46" textAnchor="middle">{value}</text>
    </svg>
  )
}

function App() {
  return (
    <div className="dashboard-page">
      <header className="top-bar">
        <div className="user-chip">
          <button className="plus-button" type="button" aria-label="Add">
            +
          </button>
          <span className="user-name">Elisa Nilson</span>
        </div>

        <nav className="section-nav" aria-label="Dashboard sections">
          <button className="section-nav-item is-selected" type="button">Dashboard</button>
          <button className="section-nav-item" type="button">Patients</button>
          <button className="section-nav-item" type="button">Doctors</button>
          <button className="section-nav-item" type="button">Schedules</button>
        </nav>

        <div className="top-actions">
          <button className="icon-button" type="button" aria-label="Notifications">
            <span className="bell-dot" />
          </button>
          <button className="icon-button" type="button" aria-label="Menu">
            <span className="menu-lines" />
          </button>
        </div>
      </header>

      <section className="title-row">
        <div>
          <h1>HealthCare DashBoard</h1>
          <p>Manage patient care, medications, vital checks, and shift tasks from one place.</p>
        </div>
        <div className="facility-line">
          <strong>St. Mary&apos;s Medical Center</strong>
          <span>Thursday, 18 December 2025</span>
        </div>
      </section>

      <main className="dashboard-grid">
        <article className="card care-overview-card">
          <div className="card-heading">
            <h2>Patient Care Overview</h2>
            <span className="week-pill">This Week</span>
          </div>
          <p className="progress-label">Total progress</p>
          <div className="progress-track">
            <div className="progress-fill" />
            <span className="progress-marker">On Track</span>
          </div>
          <div className="progress-scale">
            <span>0%</span>
            <span>45%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
          <div className="stat-row">
            {careStats.map((stat) => (
              <div className="stat-card" key={stat.label}>
                <div
                  className="stat-ring"
                  style={{ "--ring-progress": `${stat.progress}%` }}
                />
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="card doctor-card">
          <h2>Doctor</h2>
          <ul className="doctor-list">
            {doctors.map((doctor) => (
              <li key={doctor.name}>
                <span className="avatar" aria-hidden="true" />
                <span>
                  <strong>{doctor.name}</strong>
                  <small>{doctor.specialty}</small>
                </span>
                <em className={`status-pill status-${doctor.status.replace(" ", "-").toLowerCase()}`}>
                  {doctor.status}
                </em>
              </li>
            ))}
          </ul>
        </article>

        <article className="card appointment-card">
          <div className="card-heading">
            <h2>Appointments <span className="count-badge">3</span></h2>
            <button className="text-button" type="button">+ Add new</button>
          </div>
          <ul className="appointment-list">
            {appointments.map((appointment) => (
              <li key={appointment.time}>
                <time>{appointment.time}</time>
                <span>
                  <strong>{appointment.patientName}</strong>
                  <small>{appointment.visitType}</small>
                </span>
              </li>
            ))}
          </ul>
        </article>

        <article className="card recovery-card">
          <div className="recovery-top">
            <strong>86%</strong>
            <span><i className="legend-recovery" /> Recovery</span>
            <span><i className="legend-target" /> Target</span>
          </div>
          <svg className="sparkline" viewBox="0 0 180 70" aria-hidden="true">
            <path d="M5 50 C 30 48, 40 30, 60 34 S 90 55, 110 28 S 150 18, 175 22" />
            <circle cx="112" cy="28" r="4" />
          </svg>
          <p>Recovery progress trend</p>
        </article>

        <article className="card shift-card">
          <div className="card-heading">
            <h2>Shift Info</h2>
            <span className="week-pill">Today</span>
          </div>
          <div className="shift-stats">
            <div>
              <span>Critical Care</span>
              <strong>8</strong>
              <small>Patients</small>
              <b>60%</b>
            </div>
            <div>
              <span>General Ward</span>
              <strong>20</strong>
              <small>Patients</small>
              <b>+2 new today</b>
            </div>
          </div>
          <p className="shift-remaining">3h 0m remaining</p>
        </article>

        <article className="card flow-card">
          <h2>Patient Flow</h2>
          <div className="donut">
            <div>
              <strong>900</strong>
              <span>100% Capacity</span>
            </div>
          </div>
          <p className="flow-side-number">400</p>
          <p className="flow-legend">
            <span><i className="legend-recovery" /> Current Status</span>
            <span><i className="legend-target" /> Target health</span>
          </p>
        </article>

        <article className="card assistant-card">
          <h2>AI Assistant</h2>
          <div className="assistant-chips">
            <span>Why is my HIV low?</span>
            <span>Why is my HIV low?</span>
          </div>
          <p className="assistant-credits">200 Credits Remaining <button type="button">Upgrade</button></p>
          <form className="assistant-form" onSubmit={(event) => event.preventDefault()}>
            <input type="text" placeholder="Ask anything..." aria-label="Ask anything" readOnly />
            <button type="submit" aria-label="Send">↑</button>
          </form>
        </article>
      </main>

      <section className="revenue-section" aria-label="Revenue cycle">
        <div className="title-row">
          <div>
            <h2 className="revenue-title">Healthcare Revenue Cycle Dashboard - City General Hospital</h2>
          </div>
          <div className="facility-line">
            <span>Last Updated: Today 10:45 AM</span>
            <span className="week-pill">today</span>
          </div>
        </div>

        <div className="revenue-metrics">
          {revenueMetrics.map((metric) => (
            <article className="card metric-card" key={metric.label}>
              <h3>{metric.label}</h3>
              <HalfGauge fill={metric.fill} value={metric.value} />
              <p>{metric.change}</p>
              <p className={`tone-pill tone-${metric.tone}`}>{metric.target}</p>
            </article>
          ))}
        </div>

        <div className="revenue-charts">
          <article className="card">
            <h3>Detailed Denial Reasons (Last 30 Days)</h3>
            <div className="denial-chart">
              {denialReasons.map((reason) => (
                <div key={reason.label}>
                  <span style={{ height: `${reason.percent * 3}px` }} />
                  <strong>{reason.percent}%</strong>
                  <small>{reason.label}</small>
                </div>
              ))}
            </div>
          </article>

          <article className="card">
            <div className="card-heading">
              <h3>AR Aging Buckets (Current vs Target)</h3>
              <span className="aging-legend">Current <i /> Target</span>
            </div>
            <div className="aging-chart">
              {agingBuckets.map((bucket) => (
                <div key={bucket.label}>
                  <div className="aging-bars">
                    <span style={{ height: `${bucket.current}px` }} />
                    <span style={{ height: `${bucket.target}px` }} />
                  </div>
                  <small>{bucket.label}</small>
                </div>
              ))}
            </div>
          </article>
        </div>

        <article className="card milestone-card">
          <h3>Claims Lifecycle Milestone Tracker (Denial Focus)</h3>
          <ol className="milestone-track">
            {claimMilestones.map((milestone) => (
              <li key={milestone.name}>
                <strong>{milestone.name}</strong>
                <span>{milestone.date}</span>
                <em className={`tone-pill tone-${milestone.state.replace(" ", "-").toLowerCase()}`}>
                  {milestone.state}
                </em>
              </li>
            ))}
          </ol>
        </article>
      </section>
    </div>
  )
}

export default App
