"use client";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import type { GeoResult } from "@/lib/types";

// Iconos de Leaflet vía CDN (evita el problema de assets en bundlers)
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapView({ results }: { results: GeoResult[] }) {
  const center: [number, number] = results.length
    ? [results[0].lat, results[0].lng]
    : [-34.6, -58.4];
  return (
    <MapContainer center={center} zoom={13} style={{ height: 400, width: "100%" }}>
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {results.map((r) => (
        <Marker key={r.osm_id} position={[r.lat, r.lng]} icon={icon}>
          <Popup>{r.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
