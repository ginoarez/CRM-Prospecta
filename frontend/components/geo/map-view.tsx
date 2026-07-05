"use client";
import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import type { GeoResult } from "@/lib/types";
import BusinessPopup from "@/components/geo/business-popup";

const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export interface MapFocus { osmId: string; ts: number }

function FocusHandler({ focus, markers }: { focus: MapFocus | null; markers: React.MutableRefObject<Map<string, L.Marker>> }) {
  const map = useMap();
  useEffect(() => {
    if (!focus) return;
    const m = markers.current.get(focus.osmId);
    if (!m) return;
    map.flyTo(m.getLatLng(), Math.max(map.getZoom(), 15), { duration: 0.6 });
    m.openPopup();
  }, [focus, map, markers]);
  return null;
}

export default function MapView({ results, focus, onImport, importedIds, importingId, importError }: {
  results: GeoResult[];
  focus: MapFocus | null;
  onImport: (r: GeoResult) => void;
  importedIds: Set<string>;
  importingId: string | null;
  importError: string | null;
}) {
  const markers = useRef(new Map<string, L.Marker>());
  const center: [number, number] = results.length ? [results[0].lat, results[0].lng] : [-34.6, -58.4];
  return (
    <MapContainer center={center} zoom={13} style={{ height: 400, width: "100%" }} className="geo-map">
      <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <FocusHandler focus={focus} markers={markers} />
      {results.map((r) => (
        <Marker key={r.osm_id} position={[r.lat, r.lng]} icon={icon}
                ref={(m) => { if (m) markers.current.set(r.osm_id, m); }}>
          <Popup maxWidth={280}>
            <BusinessPopup r={r} onImport={onImport}
              imported={r.already_imported || importedIds.has(r.osm_id)}
              importing={importingId === r.osm_id}
              error={importError} />
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
