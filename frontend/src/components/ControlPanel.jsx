import React from 'react';
import styled from 'styled-components';

const Panel = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
  z-index: 1;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 18px;
`;

const ConnectionStatus = styled.div`
  display: flex;
  align-items: center;
`;

const StatusIndicator = styled.div`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: ${props => props.connected ? '#4CAF50' : '#F44336'};
  margin-right: 8px;
`;

const Section = styled.div`
  margin-bottom: 16px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
`;

const EventList = styled.div`
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 8px;
`;

const EventItem = styled.div`
  padding: 8px;
  border-bottom: 1px solid #eee;
  font-size: 12px;
  
  &:last-child {
    border-bottom: none;
  }
`;

const Stat = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    border-bottom: none;
  }
`;

function ControlPanel({ isConnected, vehicleCount, geofenceEvents }) {
  return (
    <Panel>
      <Header>
        <Title>Delivery Tracker</Title>
        <ConnectionStatus>
          <StatusIndicator connected={isConnected} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </ConnectionStatus>
      </Header>
      
      <Section>
        <SectionTitle>Statistics</SectionTitle>
        <Stat>
          <span>Active Vehicles:</span>
          <span>{vehicleCount}</span>
        </Stat>
        <Stat>
          <span>Geofence Events:</span>
          <span>{geofenceEvents.length}</span>
        </Stat>
      </Section>
      
      <Section>
        <SectionTitle>Recent Geofence Events</SectionTitle>
        <EventList>
          {geofenceEvents.length === 0 ? (
            <EventItem>No events yet</EventItem>
          ) : (
            geofenceEvents.slice(-10).reverse().map((event, index) => (
              <EventItem key={index}>
                <div><strong>Vehicle:</strong> {event.vehicle_id}</div>
                <div><strong>Zone:</strong> {event.geofence_name}</div>
                <div><strong>Event:</strong> {event.is_inside ? 'Entered' : 'Exited'}</div>
                <div><strong>Time:</strong> {new Date(event.timestamp).toLocaleTimeString()}</div>
              </EventItem>
            ))
          )}
        </EventList>
      </Section>
    </Panel>
  );
}

export default ControlPanel;
