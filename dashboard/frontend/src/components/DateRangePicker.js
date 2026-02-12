import React from "react";

function DateRangePicker({ dateRange, setDateRange }) {
  return (
    <div className="date-picker">
      <label>
        Start Date:
        <input
          type="date"
          value={dateRange.start}
          onChange={(e) =>
            setDateRange({ ...dateRange, start: e.target.value })
          }
        />
      </label>
      <label>
        End Date:
        <input
          type="date"
          value={dateRange.end}
          onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
        />
      </label>
    </div>
  );
}

export default DateRangePicker;
