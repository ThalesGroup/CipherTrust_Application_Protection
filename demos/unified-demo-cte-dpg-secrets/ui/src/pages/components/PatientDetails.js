import React, {useEffect, useState} from "react";
import moment from "moment-timezone";
import Datetime from "react-datetime";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArchive, faBoxOpen, faCalendar, faCalendarAlt, faCartArrowDown, faChartPie, faChevronDown, faClipboard, faCommentDots, faDiagnoses, faDownload, faFile, faFileAlt, faPlus, faPrescription, faRocket, faStore, faVoicemail } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Dropdown, Modal, Form, InputGroup } from '@themesberg/react-bootstrap';
import { ChoosePhotoWidget, ProfileCardWidget } from "../../components/Widgets";
import { GeneralInfoForm } from "../../components/Forms";
import axios from "axios";
import Profile3 from "../../assets/img/team/profile-picture-3.jpg";
import Profile1 from "../../assets/img/team/profile-picture-1.jpg";
import ProfileCover from "../../assets/img/profile-cover.jpg";

const PatientDetails = (props) => {
  console.log(props.location.state.uid)
  var date = new Date();
  var yesterday = moment().subtract(1, 'days');
  //console.log(yesterday._d);
  var tomorrow = date.setDate(date.getDate() + 1);

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

  const [patient, setPatient] = useState("");
  const [doctors, setDoctors] = useState("");
  useEffect(() => {
    let accessToken = sessionStorage.getItem('__T__');
    let url_get_patient = 'http://localhost:8080/api/patients?id=' + props.location.state.uid
    let url_get_doctors = 'http://localhost:8080/api/doctors'

    axios
        .get(url_get_patient, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          setPatient(res.data[0]);
        })
        .catch((err) => console.log(err));
    
    axios
        .get(url_get_doctors, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          setDoctors(res.data);
        })
        .catch((err) => console.log(err));
  }, []);

  const doctors_select_values = {};
  for (const doctor of doctors) {
    if (doctor.id in doctors_select_values) {
      doctors_select_values[doctor.id].push(doctor);
    } else {
      doctors_select_values[doctor.id] = [doctor];
    }
  }

  const [showAppointmentModal, setShowAppointmentModal] = useState(false);
  const handleAppointmentModalClose = () => setShowAppointmentModal(false);

  const [doctorId, setDoctorId] = useState('');
  const [patientId, setPatientId] = useState(props.location.state.uid);
  const [appointmentDate, setAppointmentDate] = useState('01/10/2024');
  const [diagnosis, setDiagnosis] = useState('Flu')

  //Save Appointment Data
  async function addAppointment(data) {
    console.log(JSON.stringify(data))
  }

  const submitAppointment = async event => {
    event.preventDefault();
    const record = await addAppointment({
      doctorId,
      patientId,
      appointmentDate,
      diagnosis
    });
    setShowAppointmentModal(false)
  };

  return (
    <>
      <Modal as={Modal.Dialog} centered show={showAppointmentModal} onHide={handleAppointmentModalClose}>
        <Modal.Header>
          <Modal.Title className="h6">Create an Appointment</Modal.Title>
          <Button variant="close" aria-label="Close" onClick={handleAppointmentModalClose} />
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={4} className="mb-3">Patient Name: </Col>
              <Col md={8} className="mb-3">{patient.firstName} {patient.lastName}</Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Label>Physician</Form.Label>
                {/* Select from the doctors list */}
                <Form.Select 
                  defaultValue="1"
                  onChange={e => setDoctorId(e.target.value)}
                  value={doctorId}>
                  <option value="">Select</option>
                  {
                    Object.entries(doctors_select_values).map((entry) => {
                      const row = entry[0];
                      const details = entry[1];
                      return(
                        <option value={row}>{details[0].firstName} {details[0].lastName}</option>      
                      )
                    })
                  }
                </Form.Select>
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
              <Form.Label>Select Date for Appointment</Form.Label>
                <Datetime
                  timeFormat={false}
                  onChange={setAppointmentDate}
                  renderInput={(props, openCalendar) => (
                    <InputGroup>
                      <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                      <Form.Control
                        required
                        type="text"
                        value={appointmentDate ? moment(appointmentDate).format("MM/DD/YYYY") : ""}
                        placeholder="mm/dd/yyyy"
                        onFocus={openCalendar}
                        onChange={e => setAppointmentDate(e.target.value)} />
                    </InputGroup>
                  )} 
                />
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group id="diagnosis">
                  <Form.Label>First Name</Form.Label>
                  <Form.Control 
                    required 
                    type="text" 
                    placeholder="Enter patient symptoms" 
                    defaultValue={diagnosis} 
                    onChange={e => setDiagnosis(e.target.value)}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={submitAppointment}>
            Submit
        </Button>
          <Button variant="link" className="text-gray ms-auto" onClick={handleAppointmentModalClose}>
            Cancel
        </Button>
        </Modal.Footer>
      </Modal>

      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <Dropdown>
          <Dropdown.Toggle as={Button} variant="secondary" className="text-dark me-2">
            <FontAwesomeIcon icon={faPlus} className="me-2" />
            <span>New</span>
          </Dropdown.Toggle>
          <Dropdown.Menu className="dashboard-dropdown dropdown-menu-left mt-2">
            <Dropdown.Item>
              <Button className="my-1" onClick={() => setShowAppointmentModal(true)}>
                <FontAwesomeIcon icon={faDiagnoses} className="me-2" /> Lab Request
              </Button>
            </Dropdown.Item>
            <Dropdown.Item>
              <Button className="my-1" onClick={() => setShowAppointmentModal(true)}>
                <FontAwesomeIcon icon={faCalendar} className="me-2" /> Appointment
              </Button>
            </Dropdown.Item>
            <Dropdown.Item>
              <Button className="my-1" onClick={() => setShowAppointmentModal(true)}>
                <FontAwesomeIcon icon={faPrescription} className="me-2" /> Prescription
              </Button>
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
            <Card border="light" className="text-center p-0 mb-4">
              <div style={{ backgroundImage: `url(${ProfileCover})` }} className="profile-cover rounded-top" />
              <Card.Body className="pb-5">
                <Card.Img src={Profile1} alt="Neil Portrait" className="user-avatar large-avatar rounded-circle mx-auto mt-n7 mb-4" />
                <Card.Title>{patient.firstName} {patient.lastName}</Card.Title>
                <Card.Subtitle className="fw-normal">Last contacted at: </Card.Subtitle>
                <Card.Text className="text-gray mb-4">{patient.city}, {patient.state}</Card.Text>

                <Button variant="primary" size="sm" className="me-2">
                  <FontAwesomeIcon icon={faCalendar} className="me-1" /> Schedule Appointment
                </Button>
                <Button variant="secondary" size="sm">
                  <FontAwesomeIcon icon={faVoicemail} className="me-1" /> Send Message
                </Button>
              </Card.Body>
            </Card>
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
                        <td>{patient.firstName} {patient.lastName}</td>
                      </tr>
                      <tr>
                        <td>Date Of Birth</td>
                        <td>{patient.dateOfBirth}</td>
                      </tr>
                      <tr>
                        <td>Contact Number</td>
                        <td>{patient.contactNumber}</td>
                      </tr>
                      <tr>
                        <td>Email</td>
                        <td>{patient.email}</td>
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
                        <td>{patient.healthCardNumber}</td>
                      </tr>
                      <tr>
                        <td>Health Card Expiry</td>
                        <td>{patient.healthCardExpiry}</td>
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