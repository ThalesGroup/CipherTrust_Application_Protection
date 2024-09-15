import React, {useEffect, useState} from "react";
import { useHistory } from "react-router-dom";
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
  let accessToken = sessionStorage.getItem('__T__');
  let host="localhost"
  let port="8080"
  if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
      host=process.env.REACT_APP_BACKEND_IP_ADDRESS
      port=process.env.REACT_APP_BACKEND_PORT
  }
  let url_get_patient = 'http://'+host+':'+port+'/api/patients?id=' + props.location.state.uid
  let url_get_doctors = 'http://'+host+':'+port+'/api/doctors'
  let url_get_appointments = 'http://'+host+':'+port+'/api/appointments?patient_id=' + props.location.state.uid
  let url_get_lab_reports = 'http://'+host+':'+port+'/api/lab-requests?patient_id=' + props.location.state.uid
  let url_get_prescriptions = 'http://'+host+':'+port+'/api/prescriptions?patient_id=' + props.location.state.uid

  const history = useHistory();
  var current = new Date();
  var nextDay = new Date(current.getTime() + 86400000);
  var previousDay = new Date(current.getTime() + 86400000);
  var tomorrow = moment(nextDay.toLocaleString()).format("MM/DD/YYYY");
  var yesterday = moment(previousDay.toLocaleString()).format("MM/DD/YYYY");

  const [showAppointmentModal, setShowAppointmentModal] = useState(false);
  const [showLabRequestModal, setShowLabRequestModal] = useState(false);
  const [showPrescriptionModal, setShowPrescriptionModal] = useState(false);
  const [appointmentsList, setAppointmentsList] = useState('');
  const [labRequestsList, setLabRequestsList] = useState('');
  const [prescriptionsList, setPrescriptionsList] = useState('');
  
  const [patientDetails, setPatientDetails] = useState("");
  const [doctors, setDoctors] = useState("");
  const [patientAppointments, setPatientAppointments] = useState("");
  const [doctor, setDoctor] = useState('');
  const [patient, setPatient] = useState(props.location.state.uid);
  const [appointmentDate, setAppointmentDate] = useState(tomorrow);
  const [appointmentReason, setAppointmentReason] = useState('Flu');
  const [labRequisitionDate, setLabRequisitionDate] = useState('01/10/2024');
  const [symptoms, setSymptoms] = useState('Stiff Back');
  const [prescriptionDate, setPrescriptionDate] = useState(yesterday);
  const [prescriptionLength, setPrescriptionLength] = useState('90');
  const [selectedFile, setSelectedFile] = useState('');

  const handleAppointmentModalClose = () => setShowAppointmentModal(false);
  const handleLabRequestModalClose = () => setShowLabRequestModal(false);
  const handlePrescriptionModalClose = () => setShowPrescriptionModal(false);

  const onFileChange = (event) => {
    console.log(event.target.files[0]);
    setSelectedFile(event.target.files[0]);
  };

  //Save Appointment Data
  async function addAppointment(data) {
    axios.post('http://'+host+':'+port+'/api/appointments', data)
    .then((response) => {
      console.log(response);
    });
  }

  const submitAppointment = async event => {
    event.preventDefault();
    
    const record = await addAppointment({
      doctor,
      patient,
      appointmentDate,
      appointmentReason
    });
    axios
      .get(url_get_appointments, { headers: {"Authorization" : `Bearer ${sessionStorage.getItem('__T__')}`} })
      .then((res) => {
        const appointments_list = {};
        for (const appointment of res.data) {
          if (appointment.id in appointments_list) {
            appointments_list[appointment.id].push(appointment);
          } else {
            appointments_list[appointment.id] = [appointment];
          }
        }
        setAppointmentsList(appointments_list);
      })
      .catch((err) => console.log(err));
    setShowAppointmentModal(false)
    history.push('/records/patients');
  };

  //Save Lab Result
  async function addLabResult(data) {
    axios({
      method: "post",
      url: 'http://'+host+':'+port+'/api/lab-requests-attachment', 
      data: data,
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((response) => {
      console.log(response);
    });
  }

  const submitLabResultUpload = async event => {
    event.preventDefault();
    const formData = new FormData();
    // Update the formData object
    formData.append(
        "file",
        selectedFile,
        selectedFile.name
    );
    formData.append("doctor", doctor);
    formData.append("patient", patient);
    formData.append("labRequisitionDate", labRequisitionDate);
    formData.append("symptoms", symptoms);

    const record = await addLabResult(formData);
    axios
      .get(url_get_lab_reports, { headers: {"Authorization" : `Bearer ${sessionStorage.getItem('__T__')}`} })
      .then((res) => {
        const reports_list = {};
        for (const report of res.data) {
          if (report.id in reports_list) {
            reports_list[report.id].push(report);
          } else {
            reports_list[report.id] = [report];
          }
        }
        setLabRequestsList(reports_list);
      })
      .catch((err) => console.log(err));
      setShowLabRequestModal(false)      
      history.push('/records/patients');
  };

  //Save Prescription
  async function addPrescription(data) {
    axios.post('http://'+host+':'+port+'/api/prescriptions', data)
    .then((response) => {
      console.log(response);
    });
  }

  const submitPrescription = async event => {
    event.preventDefault();
    const record = await addPrescription({
      doctor,
      patient,
      prescriptionDate,
      prescriptionLength
    });    
    axios
      .get(url_get_prescriptions, { headers: {"Authorization" : `Bearer ${sessionStorage.getItem('__T__')}`} })
      .then((res) => {
        const prescriptions_list = {};
        for (const prescription of res.data) {
          if (prescription.id in prescriptions_list) {
            prescriptions_list[prescription.id].push(prescription);
          } else {
            prescriptions_list[prescription.id] = [prescription];
          }
        }
        setPrescriptionsList(prescriptions_list);
      })
      .catch((err) => console.log(err));
      setShowPrescriptionModal(false)      
      history.push('/records/patients');
  };

  useEffect(() => {
    axios
        .get(url_get_patient, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          setPatientDetails(res.data[0]);
        })
        .catch((err) => console.log(err));
    
    axios
        .get(url_get_doctors, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          setDoctors(res.data);
        })
        .catch((err) => console.log(err));
    
    axios
        .get(url_get_appointments, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          const appointments_list = {};
          for (const appointment of res.data) {
            if (appointment.id in appointments_list) {
              appointments_list[appointment.id].push(appointment);
            } else {
              appointments_list[appointment.id] = [appointment];
            }
          }
          console.log(appointments_list);
          setAppointmentsList(appointments_list);
        })
        .catch((err) => console.log(err));
    
    axios
        .get(url_get_lab_reports, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          const reports_list = {};
          for (const report of res.data) {
            if (report.id in reports_list) {
              reports_list[report.id].push(report);
            } else {
              reports_list[report.id] = [report];
            }
          }
          setLabRequestsList(reports_list);
        })
        .catch((err) => console.log(err));
    
    axios
        .get(url_get_prescriptions, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          const prescriptions_list = {};
          for (const prescription of res.data) {
            if (prescription.id in prescriptions_list) {
              prescriptions_list[prescription.id].push(prescription);
            } else {
              prescriptions_list[prescription.id] = [prescription];
            }
          }
          setPrescriptionsList(prescriptions_list);
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
  return (
    <>
      {/* Modal Box for adding new appointment */}
      <Modal as={Modal.Dialog} centered show={showAppointmentModal} onHide={handleAppointmentModalClose}>
        <Modal.Header>
          <Modal.Title className="h6">Create an Appointment</Modal.Title>
          <Button variant="close" aria-label="Close" onClick={handleAppointmentModalClose} />
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={4} className="mb-3">Patient Name: </Col>
              <Col md={8} className="mb-3">{patientDetails.firstName} {patientDetails.lastName}</Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Label>Physician</Form.Label>
                {/* Select from the doctors list */}
                <Form.Select 
                  defaultValue="1"
                  onChange={e => setDoctor(e.target.value)}
                  value={doctor}>
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
                  <Form.Label>Symptoms</Form.Label>
                  <Form.Control 
                    required 
                    type="text" 
                    placeholder="Enter patient symptoms" 
                    defaultValue={appointmentReason} 
                    onChange={e => setAppointmentReason(e.target.value)}
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

      {/* Modal Box for adding new prescription */}
      <Modal as={Modal.Dialog} centered show={showPrescriptionModal} onHide={handlePrescriptionModalClose}>
        <Modal.Header>
          <Modal.Title className="h6">Create new prescription</Modal.Title>
          <Button variant="close" aria-label="Close" onClick={handlePrescriptionModalClose} />
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={4} className="mb-3">Patient Name: </Col>
              <Col md={8} className="mb-3">{patientDetails.firstName} {patientDetails.lastName}</Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Label>Physician</Form.Label>
                {/* Select from the doctors list */}
                <Form.Select 
                  defaultValue="1"
                  onChange={e => setDoctor(e.target.value)}
                  value={doctor}>
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
              <Form.Label>Select Date for Prescription</Form.Label>
                <Datetime
                  timeFormat={false}
                  onChange={setPrescriptionDate}
                  renderInput={(props, openCalendar) => (
                    <InputGroup>
                      <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                      <Form.Control
                        required
                        type="text"
                        value={prescriptionDate ? moment(prescriptionDate).format("MM/DD/YYYY") : ""}
                        placeholder="mm/dd/yyyy"
                        onFocus={openCalendar}
                        onChange={e => setPrescriptionDate(e.target.value)} />
                    </InputGroup>
                  )} 
                />
              </Col>
            </Row>            
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group id="length">
                  <Form.Label>Prescription Length</Form.Label>
                  <Form.Control 
                    required 
                    type="text" 
                    placeholder="Enter Length of Prescriptions" 
                    defaultValue={prescriptionLength} 
                    onChange={e => setPrescriptionLength(e.target.value)}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={submitPrescription}>
            Submit
        </Button>
          <Button variant="link" className="text-gray ms-auto" onClick={handlePrescriptionModalClose}>
            Cancel
        </Button>
        </Modal.Footer>
      </Modal>

      {/* Modal Box for adding new Lab Request*/}
      <Modal as={Modal.Dialog} centered show={showLabRequestModal} onHide={handleLabRequestModalClose}>
        <Modal.Header>
          <Modal.Title className="h6">Upload Lab Test Report</Modal.Title>
          <Button variant="close" aria-label="Close" onClick={handleLabRequestModalClose} />
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={4} className="mb-3">Patient Name: </Col>
              <Col md={8} className="mb-3">{patientDetails.firstName} {patientDetails.lastName}</Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Label>Physician</Form.Label>
                {/* Select from the doctors list */}
                <Form.Select 
                  defaultValue="1"
                  onChange={e => setDoctor(e.target.value)}
                  value={doctor}>
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
              <Form.Label>Lab Test Requisition Date</Form.Label>
                <Datetime
                  timeFormat={false}
                  onChange={setLabRequisitionDate}
                  renderInput={(props, openCalendar) => (
                    <InputGroup>
                      <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                      <Form.Control
                        required
                        type="text"
                        value={labRequisitionDate ? moment(labRequisitionDate).format("MM/DD/YYYY") : ""}
                        placeholder="mm/dd/yyyy"
                        onFocus={openCalendar}
                        onChange={e => setLabRequisitionDate(e.target.value)} />
                    </InputGroup>
                  )} 
                />
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group id="symptoms">
                  <Form.Label>Symptoms</Form.Label>
                  <Form.Control 
                    required 
                    type="text" 
                    placeholder="Enter patient symptoms" 
                    defaultValue={symptoms} 
                    onChange={e => setSymptoms(e.target.value)}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group id="prescriptionPDF">
                  <Form.Label>Upload Prescription</Form.Label>
                  <Form.Control 
                    required 
                    type="file" 
                    onChange={e => onFileChange(e)}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={submitLabResultUpload}>
            Submit
        </Button>
          <Button variant="link" className="text-gray ms-auto" onClick={handleLabRequestModalClose}>
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
              <Button className="my-1" onClick={() => setShowLabRequestModal(true)}>
                <FontAwesomeIcon icon={faDiagnoses} className="me-2" /> Lab Request
              </Button>
            </Dropdown.Item>
            <Dropdown.Item>
              <Button className="my-1" onClick={() => setShowAppointmentModal(true)}>
                <FontAwesomeIcon icon={faCalendar} className="me-2" /> Appointment
              </Button>
            </Dropdown.Item>
            <Dropdown.Item>
              <Button className="my-1" onClick={() => setShowPrescriptionModal(true)}>
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
                <Card.Title>{patientDetails.firstName} {patientDetails.lastName}</Card.Title>
                <Card.Subtitle className="fw-normal">Last contacted at: {yesterday}</Card.Subtitle>
                <Card.Text className="text-gray mb-4">{patientDetails.city}, {patientDetails.state}</Card.Text>

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
                        <td>{patientDetails.firstName} {patientDetails.lastName}</td>
                      </tr>
                      <tr>
                        <td>Date Of Birth</td>
                        <td>{patientDetails.dateOfBirth}</td>
                      </tr>
                      <tr>
                        <td>Contact Number</td>
                        <td>{patientDetails.contactNumber}</td>
                      </tr>
                      <tr>
                        <td>Email</td>
                        <td>{patientDetails.email}</td>
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
                        <td>{patientDetails.healthCardNumber}</td>
                      </tr>
                      <tr>
                        <td>Health Card Expiry</td>
                        <td>{patientDetails.healthCardExpiry}</td>
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
                        <td>{patientDetails.bloodGroup}</td>
                      </tr>
                      <tr>
                        <td>Major Ailments</td>
                        <td>{patientDetails.ailments}</td>
                      </tr>
                      <tr>
                        <td>Physician</td>
                        <td>Dr. {patientDetails.primaryPhysician}</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Appointments</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Last Appointment</th>
                        <th className="border-0">Doctor</th>
                        <th className="border-0">Symtoms</th>
                        <th className="border-0">Re-schedule</th>
                      </tr>
                    </thead>
                    <tbody>
                      {                        
                        Object.entries(appointmentsList).map((entry) => {
                          const row = entry[0];
                          const details = entry[1];
                          return(
                            <tr key={`appointment-${row}`}>
                              <td>{details[0].date}</td>                              
                              <td>{details[0].doctor.firstName} {details[0].doctor.lastName}</td>
                              <td>{details[0].reason}</td>
                              <td>
                                  <FontAwesomeIcon icon={faCalendar} />
                              </td>
                            </tr>
                          )
                      })}
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Prescriptions</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Date</th>
                        <th className="border-0">Length of Prescription</th>
                        <th className="border-0">Prescribing Doctor</th>
                        <th className="border-0">View</th>
                      </tr>
                    </thead>
                    <tbody>
                      {                        
                        Object.entries(prescriptionsList).map((entry) => {
                          const row = entry[0];
                          const details = entry[1];
                          return(
                            <tr key={`prescription-${row}`}>
                              <td>{details[0].prescriptionDate}</td>                              
                              <td>{details[0].durationInDays} Days</td>
                              <td>{details[0].doctor.firstName} {details[0].doctor.lastName}</td>
                              <td>
                                  <FontAwesomeIcon icon={faDownload} />
                              </td>
                            </tr>
                          )
                      })}
                    </tbody>
                  </Table>
                  <Row>&nbsp;</Row>
                  <h5 className="mb-4">Lab results</h5>
                  <Table responsive className="table-centered table-nowrap rounded mb-0">
                    <thead className="thead-light">
                      <tr>
                        <th className="border-0">Requisition Date</th>
                        <th className="border-0">Doctor</th>
                        <th className="border-0">Symptoms</th>
                        <th className="border-0">Download</th>
                      </tr>
                    </thead>
                    <tbody>
                      {                        
                        Object.entries(labRequestsList).map((entry) => {
                          const row = entry[0];
                          const details = entry[1];
                          return(
                            <tr key={`report-${row}`}>
                              <td>{details[0].requestDate}</td>                              
                              <td>{details[0].doctor.firstName} {details[0].doctor.lastName}</td>
                              <td>{details[0].symptoms}</td>
                              <td>
                                  <FontAwesomeIcon icon={faDownload} />
                              </td>
                            </tr>
                          )
                      })}
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