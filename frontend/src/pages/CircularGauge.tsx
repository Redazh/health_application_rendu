// CircularGauge.tsx
import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface CircularGaugeProps {
  value: number;
  text?: string;
}

const CircularGauge: React.FC<CircularGaugeProps> = ({ value, text }) => {
  // Computes a color gradient from red (0) to green (100)
  const getColorFromValue = (val: number) => {
    // Interpolate between red (255,0,0) and green (0,255,0)
    const red = Math.round(255 - (val * 2.55));
    const green = Math.round(val * 2.55);
    return `rgb(${red}, ${green}, 0)`;
  };

  return (
    <div style={{ width: 120, height: 120 }}>
      <CircularProgressbar
        value={value}
        text={text || `${value}%`}
        styles={buildStyles({
          pathColor: getColorFromValue(value),
          textColor: '#000',
          trailColor: '#d6d6d6',
          textSize: '16px'
        })}
      />
    </div>
  );
};

export default CircularGauge;
