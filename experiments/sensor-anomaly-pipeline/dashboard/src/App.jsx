import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, AlertTriangle, Database, RefreshCw } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function App() {
  const [readings, setReadings] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [readingsResponse, anomaliesResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/readings/recent?limit=260`),
        fetch(`${API_BASE_URL}/anomalies/recent?limit=50`),
      ]);
      if (!readingsResponse.ok || !anomaliesResponse.ok) {
        throw new Error("API request failed");
      }
      setReadings(await readingsResponse.json());
      setAnomalies(await anomaliesResponse.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 3000);
    return () => clearInterval(timer);
  }, []);

  const chartData = useMemo(() => {
    const anomalyByTime = new Map();
    for (const event of anomalies) {
      anomalyByTime.set(event.measured_at, event);
    }

    return [...readings]
      .reverse()
      .slice(-240)
      .map((item) => {
        const anomaly = anomalyByTime.get(item.measured_at);
        const temperature = Number(item.temperature.toFixed?.(1) ?? item.temperature);
        const humidity = Number(item.humidity.toFixed?.(1) ?? item.humidity);
        return {
          time: new Date(item.measured_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          device_id: item.device_id,
          temperature,
          humidity,
          anomalyTemperature: anomaly ? temperature : null,
          anomalyHumidity: anomaly ? humidity : null,
          anomalyType: anomaly?.anomaly_type ?? "",
        };
      });
  }, [readings, anomalies]);

  const deviceSummary = useMemo(() => {
    const latest = new Map();
    for (const reading of readings) {
      if (!latest.has(reading.device_id)) {
        latest.set(reading.device_id, reading);
      }
    }
    const anomalousDevices = new Set(anomalies.slice(0, 20).map((item) => item.device_id));
    return [...latest.values()].map((reading) => ({
      ...reading,
      status: anomalousDevices.has(reading.device_id) ? "ANOMALY" : "NORMAL",
    }));
  }, [readings, anomalies]);

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <h1>Sensor Anomaly Dashboard</h1>
          <p>Kafka pipeline status for simulated Chytonpide temperature and humidity streams.</p>
        </div>
        <button className="iconButton" onClick={refresh} disabled={loading} title="Refresh data">
          <RefreshCw size={18} />
        </button>
      </header>

      {error ? <div className="error">API error: {error}</div> : null}

      <section className="metrics">
        <Metric icon={<Database size={18} />} label="Readings" value={readings.length} />
        <Metric icon={<AlertTriangle size={18} />} label="Anomalies" value={anomalies.length} />
        <Metric icon={<Activity size={18} />} label="Devices" value={deviceSummary.length} />
      </section>

      <section className="layout">
        <div className="panel chartPanel">
          <h2>Recent temperature and humidity</h2>
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" minTickGap={28} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="temperature" stroke="#d94f30" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="humidity" stroke="#2576b8" dot={false} strokeWidth={2} />
              <Line
                name="Anomaly temperature"
                type="linear"
                dataKey="anomalyTemperature"
                stroke="transparent"
                dot={{ r: 6, fill: "#b42318", stroke: "#ffffff", strokeWidth: 2 }}
                activeDot={{ r: 8 }}
                connectNulls={false}
                isAnimationActive={false}
              />
              <Line
                name="Anomaly humidity"
                type="linear"
                dataKey="anomalyHumidity"
                stroke="transparent"
                dot={{ r: 6, fill: "#7a271a", stroke: "#ffffff", strokeWidth: 2 }}
                activeDot={{ r: 8 }}
                connectNulls={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h2>Device status</h2>
          <div className="deviceList">
            {deviceSummary.map((device) => (
              <div className="deviceRow" key={device.device_id}>
                <span className={`statusDot ${device.status === "ANOMALY" ? "danger" : ""}`} />
                <div>
                  <strong>{device.device_id}</strong>
                  <span>
                    {Number(device.temperature).toFixed(1)}C / {Number(device.humidity).toFixed(1)}%
                  </span>
                </div>
                <b>{device.status}</b>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>Recent anomaly events</h2>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>Detected</th>
                <th>Device</th>
                <th>Type</th>
                <th>Score</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((event) => (
                <tr key={event.id}>
                  <td>{new Date(event.detected_at).toLocaleTimeString()}</td>
                  <td>{event.device_id}</td>
                  <td>{event.anomaly_type}</td>
                  <td>{event.anomaly_score == null ? "-" : Number(event.anomaly_score).toFixed(3)}</td>
                  <td>{event.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
