import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  AnnotationElement
} from 'chart.js';
import 'chartjs-plugin-annotation';
import './App.css';

import EventSelector from './components/EventSelector';
import DateRangePicker from './components/DateRangePicker';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [prices, setPrices] = useState({ dates: [], prices: [] });
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dateRange, setDateRange] = useState({
    start: '2012-01-01',
    end: '2022-12-31'
  });
  const [highlightDate, setHighlightDate] = useState(null);

  // Load historical prices on mount + date range change
  useEffect(() => {
    axios.get(`http://localhost:5000/api/prices?start=${dateRange.start}&end=${dateRange.end}`)
      .then(res => setPrices(res.data))
      .catch(err => console.error('Error loading prices:', err));
  }, [dateRange]);

  // Load events on mount
  useEffect(() => {
    axios.get('http://localhost:5000/api/events')
      .then(res => setEvents(res.data))
      .catch(err => console.error('Error loading events:', err));
  }, []);

  // Handle event click - show impact
  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setHighlightDate(event.date);
    
    axios.get(`http://localhost:5000/api/event-impact/${event.date}`)
      .then(res => {
        setPrices({
          dates: res.data.dates,
          prices: res.data.prices
        });
        alert(`Impact: ${res.data.change_pct}% price change around ${event.date}`);
      })
      .catch(err => console.error('Error loading event impact:', err));
  };

  // Chart data configuration
  const chartData = {
    labels: prices.dates,
    datasets: [
      {
        label: 'Brent Oil Price (USD/barrel)',
        data: prices.prices,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.3,
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: highlightDate ? 
          `Brent Oil Prices (Highlight: ${highlightDate})` : 
          'Brent Oil Historical Prices',
        font: { size: 18 }
      },
      tooltip: {
        mode: 'index',
        intersect: false
      }
    },
    scales: {
      x: {
        title: { display: true, text: 'Date' },
        ticks: { maxTicksLimit: 10 }
      },
      y: {
        title: { display: true, text: 'Price (USD)' },
        beginAtZero: false
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🛢️ Brent Oil Price Dashboard</h1>
        <p>Birhan Energies | Geopolitical Event Impact Analysis</p>
      </header>

      <div className="controls">
        <DateRangePicker dateRange={dateRange} setDateRange={setDateRange} />
        <EventSelector events={events} onEventClick={handleEventClick} />
      </div>

      <div className="chart-container">
        <Line data={chartData} options={chartOptions} />
      </div>

      {selectedEvent && (
        <div className="event-detail">
          <h3>Selected Event: {selectedEvent.description}</h3>
          <p><strong>Date:</strong> {selectedEvent.date}</p>
          <p><strong>Type:</strong> {selectedEvent.event_type}</p>
          <p><strong>Region:</strong> {selectedEvent.region}</p>
          <button onClick={() => {
            setSelectedEvent(null);
            setHighlightDate(null);
            setDateRange({ start: '2012-01-01', end: '2022-12-31' });
          }}>
            Clear Selection
          </button>
        </div>
      )}
    </div>
  );
}

export default App;