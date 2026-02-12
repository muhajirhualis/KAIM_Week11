import React, { useState } from "react";

function EventSelector({ events, onEventClick }) {
  const [filterType, setFilterType] = useState("all");

  const filteredEvents =
    filterType === "all"
      ? events
      : events.filter((e) => e.event_type === filterType);

  const eventTypes = ["all", ...new Set(events.map((e) => e.event_type))];

  return (
    <div className="event-selector">
      <label>
        Filter by Type:
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          {eventTypes.map((type) => (
            <option key={type} value={type}>
              {type.replace("_", " ").toUpperCase()}
            </option>
          ))}
        </select>
      </label>

      <div className="events-list">
        <h4>Key Events ({filteredEvents.length})</h4>
        {filteredEvents.slice(0, 10).map((event, idx) => (
          <div
            key={idx}
            className="event-item"
            onClick={() => onEventClick(event)}
            title={event.description}
          >
            <strong>{event.date}</strong> • {event.event_type}
            <br />
            <small>{event.description.substring(0, 60)}...</small>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EventSelector;
