import React, { useState, useRef, useCallback } from 'react';
import { GoogleMap, LoadScript, Autocomplete, Marker } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '400px',
  border: '2px solid #000',
  borderRadius: '10px',
  margin: '0 auto',
  position: 'relative',
};

const center = {
  lat: 34.0224,
  lng: -118.2851
};

// Define map options to disable the "Map" and "Satellite" controls
const mapOptions = {
  mapTypeControl: false,
};

const MapComponent = ({ setLocation }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [autocomplete, setAutocomplete] = useState(null);
  const markerRef = useRef(null);

  const onLoad = useCallback((autocompleteInstance) => {
    setAutocomplete(autocompleteInstance);
  }, []);

  const onPlaceChanged = () => {
    if (autocomplete !== null) {
      const place = autocomplete.getPlace();
      if (place.geometry && place.geometry.location) {
        const location = {
          lat: place.geometry.location.lat(),
          lng: place.geometry.location.lng()
        };
        setSelectedLocation(location);
        setLocation(location);

        if (markerRef.current) {
          markerRef.current.setPosition(place.geometry.location);
        }
      }
    } else {
      console.log('Autocomplete is not loaded yet!');
    }
  };

  const onMapClick = (e) => {
    const location = {
      lat: e.latLng.lat(),
      lng: e.latLng.lng()
    };
    setSelectedLocation(location);
    setLocation(location);

    if (markerRef.current) {
      markerRef.current.setPosition(e.latLng);
    }
  };

  const handleMarkerDragEnd = (e) => {
    const location = {
      lat: e.latLng.lat(),
      lng: e.latLng.lng()
    };
    setSelectedLocation(location);
    setLocation(location);
  };

  return (
    <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY} libraries={['places']}>
      <div style={containerStyle}>
        <Autocomplete onLoad={onLoad} onPlaceChanged={onPlaceChanged}>
          <input
            type="text"
            placeholder="Search for a location"
            style={{
              boxSizing: 'border-box',
              border: '1px solid transparent',
              width: '240px',
              height: '32px',
              padding: '0 12px',
              borderRadius: '3px',
              boxShadow: '0 2px 6px rgba(0, 0, 0, 0.3)',
              fontSize: '14px',
              outline: 'none',
              textOverflow: 'ellipses',
              position: 'absolute',
              top: '10px',
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 1
            }}
          />
        </Autocomplete>
        <GoogleMap
          mapContainerStyle={{ width: '100%', height: '100%' }}
          center={center}
          zoom={14}
          options={mapOptions}
          onClick={onMapClick}
        >
          {selectedLocation && (
            <Marker
              position={selectedLocation}
              draggable={true}
              onDragEnd={handleMarkerDragEnd}
              ref={markerRef}
            />
          )}
        </GoogleMap>
      </div>
    </LoadScript>
  );
};

export default MapComponent;
