
import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import moment from "moment-timezone";
import Datetime from "react-datetime";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCalendarAlt } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Form, Button, InputGroup } from '@themesberg/react-bootstrap';
import axios from "axios";

export const GeneralInfoForm = () => {
  const [dateOfBirth, setDateOfBirth] = useState("01/01/1990");
  const [firstName, setFirstName] = useState('Jane');
  const [lastName, setLastName] = useState('Doe');
  const [gender, setGender] = useState('F')
  const [email, setEmail] = useState('example@ciphetrust.io')
  const [contactNumber, setContactNumber] = useState('+1 234-567-8901')
  const [address, setAddress] = useState('123 Test Dr.')
  const [houseNumber, setHouseNumber] = useState('')
  const [city, setCity] = useState('Arlington')
  const [state, setState] = useState('VA')
  const [zipCode, setZipCode] = useState('22202')
  const [healthCardNumber, setHealthCardNumber] = useState('1EG4-TE5-MK72')
  const [healthCardExpiry, setHealthCardExpiry] = useState("01/01/2025");
  const [bloodGroup, setBloodGroup] = useState('Z+');
  const [ailments, setAilments] = useState('TBD');
  const [primaryPhysician, setPrimaryPhysician] = useState('');

  const [doctors, setDoctors] = useState("");
  const history = useHistory();

  let host="localhost"
  let port="8080"
  if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
      host=process.env.REACT_APP_BACKEND_IP_ADDRESS
      port=process.env.REACT_APP_BACKEND_PORT
  }

  async function addPatientRecord(data) {
    console.log(
      JSON.stringify(data)
    )
    axios.post('http://'+host+':'+port+'/api/patients', data)
    .then((response) => {
      history.push('/records/patients');
    });
  }

  useEffect(() => {
    let accessToken = sessionStorage.getItem('__T__');
    let url_get_doctors = 'http://'+host+':'+port+'/api/doctors'  
    axios
        .get(url_get_doctors, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          console.log(res.data);
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

  const handleSubmit = async event => {
    event.preventDefault();
    const record = await addPatientRecord({
      firstName,
      lastName,
      dateOfBirth,
      gender,
      email,
      contactNumber,
      address,
      houseNumber,
      city,
      state,
      zipCode,
      healthCardNumber,
      healthCardExpiry,
      bloodGroup,
      ailments,
      primaryPhysician
    });
  };

  return (
    <Card border="light" className="bg-white shadow-sm mb-4">
      <Card.Body>
        <h5 className="mb-4">Patient information</h5>
        <Form>
          <Row>
            <Col md={6} className="mb-3">
              <Form.Group id="firstName">
                <Form.Label>First Name</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Enter your first name" 
                defaultValue={"Jane"} 
                onChange={e => setFirstName(e.target.value)}/>
              </Form.Group>
            </Col>
            <Col md={6} className="mb-3">
              <Form.Group id="lastName">
                <Form.Label>Last Name</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Also your last name" 
                defaultValue={"Doe"}
                onChange={e => setLastName(e.target.value)} />
              </Form.Group>
            </Col>
          </Row>
          <Row className="align-items-center">
            <Col md={6} className="mb-3">
              <Form.Group id="birthday">
                <Form.Label>Birthday</Form.Label>
                <Datetime
                  timeFormat={false}
                  onChange={setDateOfBirth}
                  renderInput={(props, openCalendar) => (
                    <InputGroup>
                      <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                      <Form.Control
                        required
                        type="text"
                        value={dateOfBirth ? moment(dateOfBirth).format("MM/DD/YYYY") : ""}
                        placeholder="mm/dd/yyyy"
                        onFocus={openCalendar}
                        onChange={e => setDateOfBirth(e.target.value)} />
                    </InputGroup>
                  )} />
              </Form.Group>
            </Col>
            <Col md={6} className="mb-3">
              <Form.Group id="gender">
                <Form.Label>Gender</Form.Label>
                <Form.Select 
                defaultValue="1"
                onChange={e => setGender(e.target.value)}
                value={gender}>
                  <option value="">Gender</option>
                  <option value="F">Female</option>
                  <option value="M">Male</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          <Row>
            <Col md={6} className="mb-3">
              <Form.Group id="email">
                <Form.Label>Email</Form.Label>
                <Form.Control 
                required 
                type="email" 
                placeholder="example@ciphetrust.io" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={6} className="mb-3">
              <Form.Group id="phone">
                <Form.Label>Phone</Form.Label>
                <Form.Control 
                required 
                type="text"
                value={contactNumber}
                onChange={e => setContactNumber(e.target.value)}
                />
              </Form.Group>
            </Col>
          </Row>

          <h5 className="my-4">HealthCare Information</h5>
          <Row>
            <Col sm={6} className="mb-3">
              <Form.Group id="address">
                <Form.Label>Health Card Number</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Enter your Health Card Number" 
                value={healthCardNumber}
                onChange={e => setHealthCardNumber(e.target.value)} 
                />
              </Form.Group>
            </Col>
            <Col sm={6} className="mb-3">
              <Form.Group id="addressNumber">
                <Form.Label>Health Card Expiry</Form.Label>
                <Datetime
                  timeFormat={false}
                  onChange={setHealthCardExpiry}
                  renderInput={(props, openCalendar) => (
                    <InputGroup>
                      <InputGroup.Text><FontAwesomeIcon icon={faCalendarAlt} /></InputGroup.Text>
                      <Form.Control
                        required
                        type="text"
                        value={healthCardExpiry ? moment(healthCardExpiry).format("MM/DD/YYYY") : ""}
                        placeholder="mm/dd/yyyy"
                        onFocus={openCalendar}
                        onChange={e => setHealthCardExpiry(e.target.value)} />
                    </InputGroup>
                  )} 
                />
              </Form.Group>
            </Col>
          </Row>

          <h5 className="my-4">Medical Information</h5>
          <Row>
            <Col sm={4} className="mb-3">
              <Form.Group id="bloodGroup">
                <Form.Label>Blood Group</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Enter your Blood Group" 
                value={bloodGroup}
                onChange={e => setBloodGroup(e.target.value)} 
                />
              </Form.Group>
            </Col>
            <Col sm={4} className="mb-3">
              <Form.Group id="ailments">
                <Form.Label>Existing Conditions</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Any existing conditions" 
                value={ailments}
                onChange={e => setAilments(e.target.value)} 
                />
              </Form.Group>
            </Col>
            <Col sm={4} className="mb-3">
              <Form.Group id="primaryPhysician">
                <Form.Label>Select Physician</Form.Label>
                <Form.Select 
                  defaultValue="1"
                  onChange={e => setPrimaryPhysician(e.target.value)}
                  value={primaryPhysician}>
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
              </Form.Group>
            </Col>
          </Row>

          <h5 className="my-4">Address</h5>
          <Row>
            <Col sm={9} className="mb-3">
              <Form.Group id="address">
                <Form.Label>Address</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Enter your home address" 
                value={address}
                onChange={e => setAddress(e.target.value)} 
                />
              </Form.Group>
            </Col>
            <Col sm={3} className="mb-3">
              <Form.Group id="addressNumber">
                <Form.Label>House Number</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="Number" 
                value={houseNumber}
                onChange={e => setHouseNumber(e.target.value)} 
                />
              </Form.Group>
            </Col>
          </Row>
          <Row>
            <Col sm={4} className="mb-3">
              <Form.Group id="city">
                <Form.Label>City</Form.Label>
                <Form.Control 
                required 
                type="text" 
                placeholder="City" 
                value={city} 
                onChange={e => setCity(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col sm={4} className="mb-3">
              <Form.Group className="mb-2">
                <Form.Label>Select state</Form.Label>
                <Form.Select 
                id="state" 
                value={state}
                onChange={e => setState(e.target.value)} >
                  <option value="0">State</option>
                  <option value="AL">Alabama</option>
                  <option value="AK">Alaska</option>
                  <option value="AZ">Arizona</option>
                  <option value="AR">Arkansas</option>
                  <option value="CA">California</option>
                  <option value="CO">Colorado</option>
                  <option value="CT">Connecticut</option>
                  <option value="DE">Delaware</option>
                  <option value="DC">District Of Columbia</option>
                  <option value="FL">Florida</option>
                  <option value="GA">Georgia</option>
                  <option value="HI">Hawaii</option>
                  <option value="ID">Idaho</option>
                  <option value="IL">Illinois</option>
                  <option value="IN">Indiana</option>
                  <option value="IA">Iowa</option>
                  <option value="KS">Kansas</option>
                  <option value="KY">Kentucky</option>
                  <option value="LA">Louisiana</option>
                  <option value="ME">Maine</option>
                  <option value="MD">Maryland</option>
                  <option value="MA">Massachusetts</option>
                  <option value="MI">Michigan</option>
                  <option value="MN">Minnesota</option>
                  <option value="MS">Mississippi</option>
                  <option value="MO">Missouri</option>
                  <option value="MT">Montana</option>
                  <option value="NE">Nebraska</option>
                  <option value="NV">Nevada</option>
                  <option value="NH">New Hampshire</option>
                  <option value="NJ">New Jersey</option>
                  <option value="NM">New Mexico</option>
                  <option value="NY">New York</option>
                  <option value="NC">North Carolina</option>
                  <option value="ND">North Dakota</option>
                  <option value="OH">Ohio</option>
                  <option value="OK">Oklahoma</option>
                  <option value="OR">Oregon</option>
                  <option value="PA">Pennsylvania</option>
                  <option value="RI">Rhode Island</option>
                  <option value="SC">South Carolina</option>
                  <option value="SD">South Dakota</option>
                  <option value="TN">Tennessee</option>
                  <option value="TX">Texas</option>
                  <option value="UT">Utah</option>
                  <option value="VT">Vermont</option>
                  <option value="VA">Virginia</option>
                  <option value="WA">Washington</option>
                  <option value="WV">West Virginia</option>
                  <option value="WI">Wisconsin</option>
                  <option value="WY">Wyoming</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col sm={4}>
              <Form.Group id="zip">
                <Form.Label>ZIP</Form.Label>
                <Form.Control 
                required 
                type="tel" 
                placeholder="ZIP" 
                value={zipCode}
                onChange={e => setZipCode(e.target.value)}
                />
              </Form.Group>
            </Col>
          </Row>
          <div className="mt-3">
            <Button variant="primary" type="submit" onClick={handleSubmit}>Save All</Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};
