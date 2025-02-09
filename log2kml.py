import pandas as pd
import argparse
from datetime import datetime

def generate_kml(input_csv, output_kml):
    # Load the CSV file
    df = pd.read_csv(input_csv)
    
    # Check if required columns exist
    required_columns = ['Date', 'Hour (h)', 'Minute (min)', 'Second (s)', 'Timestamp (ms)', 'GPS Latitude (°)', 'GPS Longitude (°)', 'GPS Altitude (m)', 'GPS Speed (km/h)']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Extract relevant GPS data and drop NaN values
    gps_data = df[required_columns].dropna()
    gps_data.columns = ['Date', 'Hour', 'Minute', 'Second', 'Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Speed']  # Rename columns

    # Ensure data is in correct type
    gps_data = gps_data.astype({'Date': str, 'Hour': int, 'Minute': int, 'Second': int, 'Timestamp': int, 'Latitude': float, 'Longitude': float, 'Altitude': float, 'Speed': float})

    # Create KML content
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GPS Data</name>
"""
    
    # Add placemarks
    for _, row in gps_data.iterrows():
        # Parse the date in YYMMDD format
        date_str = row['Date']
        # Format timestamp to ensure it has only 6 digits for microseconds
        timestamp_ms = str(row['Timestamp']).zfill(3)[:6]  # Pad with zeros and truncate to 6 digits
        dt_str = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]} {row['Hour']:02d}:{row['Minute']:02d}:{row['Second']:02d}.{timestamp_ms}"
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
            epoch_timestamp = int(dt.timestamp() * 1000)  # Convert to epoch timestamp in milliseconds
            iso_timestamp = dt.isoformat() + 'Z'  # Convert to ISO 8601 format

            kml_content += f"""    <Placemark>
      <name>Timestamp: {epoch_timestamp} ms</name>
      <description><![CDATA[Speed: {row['Speed']} km/h<br>Altitude: {row['Altitude']} m]]></description>
      <TimeStamp>
        <when>{iso_timestamp}</when>
      </TimeStamp>
      <Point>
        <coordinates>{row['Longitude']},{row['Latitude']},{row['Altitude']}</coordinates>
      </Point>
    </Placemark>
"""
        except ValueError:
            raise ValueError(f"Failed to parse date string: {dt_str}")

    # Close KML structure
    kml_content += """  </Document>
</kml>
"""
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_kml_with_timestamp = output_kml.replace(".kml", f"_{timestamp}.kml")
    with open(output_kml_with_timestamp, "w", encoding="utf-8") as f:
        f.write(kml_content)
    
    print(f"KML file saved as: {output_kml_with_timestamp}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV GPS data to KML format.")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("output_kml", help="Path to the output KML file")
    args = parser.parse_args()

    generate_kml(args.input_csv, args.output_kml)