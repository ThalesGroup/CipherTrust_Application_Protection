import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArchive, faBoxOpen, faCalendar, faCartArrowDown, faChartPie, faChevronDown, faClipboard, faCommentDots, faDownload, faFile, faFileAlt, faPlus, faRocket, faStore, faVoicemail } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Dropdown } from '@themesberg/react-bootstrap';
import { ChoosePhotoWidget, ProfileCardWidget } from "../../components/Widgets";
import { GeneralInfoForm } from "../../components/Forms";

import Profile3 from "../../assets/img/team/profile-picture-3.jpg";


const PatientDetails = (props) => {
  console.log(props.location.state)

  const labResults = [
    { id: 1, dateRequisition: "03/01/2024", action: faDownload },
    { id: 2, dateRequisition: "03/10/2024", action: faDownload },
  ];
  const LabResultsTableRow = (props) => {
    const { id, dateRequisition, action } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td>{dateRequisition}</td>
        <td>
            <FontAwesomeIcon icon={faDownload} />
        </td>
      </tr>
    );
  };

  const prescriptions = [
    { id: 1, primaryDiagnosis: "whatever", action: faFile },
  ];
  const PrescriptionsTableRow = (props) => {
    const { id, primaryDiagnosis, action } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td>{primaryDiagnosis}</td>
        <td>
            <FontAwesomeIcon icon={faFile} />
        </td>
      </tr>
    );
  };

  const appointments = [
    { id: 1, lastAppointment: "01/01/2024", doctor: "Dr. Jane Doe", action: faCalendar },
  ];
  const AppointmentTableRow = (props) => {
    const { id, lastAppointment, doctor, action } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td>{lastAppointment}</td>
        <td>{doctor}</td>
        <td>
            <FontAwesomeIcon icon={faCalendar} />
        </td>
      </tr>
    );
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <Dropdown>
          <Dropdown.Toggle as={Button} variant="secondary" className="text-dark me-2">
            <FontAwesomeIcon icon={faPlus} className="me-2" />
            <span>New</span>
          </Dropdown.Toggle>
          <Dropdown.Menu className="dashboard-dropdown dropdown-menu-left mt-2">
            <Dropdown.Item>
              <FontAwesomeIcon icon={faFileAlt} className="me-2" /> Lab Report
            </Dropdown.Item>
            <Dropdown.Divider />
            <Dropdown.Item>
              <FontAwesomeIcon icon={faArchive} className="text-danger me-2" /> Archive User
              </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>

        <div className="d-flex">
          <Dropdown>
            <Dropdown.Toggle as={Button} variant="primary">
              <FontAwesomeIcon icon={faClipboard} className="me-2" /> Reports
              <span className="icon icon-small ms-1"><FontAwesomeIcon icon={faChevronDown} /></span>
            </Dropdown.Toggle>
            <Dropdown.Menu className="dashboard-dropdown dropdown-menu-left mt-1">
              <Dropdown.Item>
                <FontAwesomeIcon icon={faCalendar} className="me-2" /> Appointments
              </Dropdown.Item>
              <Dropdown.Item>
                <FontAwesomeIcon icon={faVoicemail} className="me-2" /> Messages
              </Dropdown.Item>
              <Dropdown.Item>
                <FontAwesomeIcon icon={faFile} className="me-2" /> Lab Reports
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      </div>

      <Row>
        <Col xs={12} xl={12}>
          <Row>
            <Col xs={4}>
              <ProfileCardWidget />
            </Col>
            <Col xs={8}>
              <Card border="light" className="bg-white shadow-sm mb-4">
                <Card.Body>
                  <h5 className="mb-4">General information</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Info</th>
                        <th className="border-0">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>ID</td>
                        <td>{props.location.state.uid}</td>
                      </tr>
                      <tr>
                        <td>Name</td>
                        <td>John Doe</td>
                      </tr>
                      <tr>
                        <td>Date Of Birth</td>
                        <td>09/09/1999</td>
                      </tr>
                      <tr>
                        <td>Contact Number</td>
                        <td>+1 123-456-7890</td>
                      </tr>
                      <tr>
                        <td>Email</td>
                        <td>john.doe@ciphertrust.io</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Healthcare information</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Info</th>
                        <th className="border-0">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Health Card Number</td>
                        <td>123-456-7890</td>
                      </tr>
                      <tr>
                        <td>Health Card Expiry</td>
                        <td>01/01/2025</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Medical information</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Info</th>
                        <th className="border-0">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Blood Group</td>
                        <td>B+</td>
                      </tr>
                      <tr>
                        <td>Major Ailments</td>
                        <td>Whatever</td>
                      </tr>
                      <tr>
                        <td>Physician</td>
                        <td>Dr. Jane Doe</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Appointments</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">#</th>
                        <th className="border-0">Last Appointment</th>
                        <th className="border-0">Doctor</th>
                        <th className="border-0">Re-schedule</th>
                      </tr>
                    </thead>
                    <tbody>
                      {appointments.map(pt => <AppointmentTableRow key={`appointment-${pt.id}`} {...pt} />)}
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Prescriptions</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">#</th>
                        <th className="border-0">Primary Diagnosis</th>
                        <th className="border-0">View</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prescriptions.map(pt => <PrescriptionsTableRow key={`prescription-${pt.id}`} {...pt} />)}
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Lab results</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">#</th>
                        <th className="border-0">Requisition Date</th>
                        <th className="border-0">Download</th>
                      </tr>
                    </thead>
                    <tbody>
                      {labResults.map(pt => <LabResultsTableRow key={`lab-result-${pt.id}`} {...pt} />)}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </>
  );
};

export default PatientDetails;