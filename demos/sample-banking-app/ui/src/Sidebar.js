import {React, useState} from 'react';
import { faShield, faRectangleXmark, faHistory, faUser, faBook, faSearch } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import useToken from './useToken';
import jwt_decode from "jwt-decode";
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { useNavigate } from 'react-router-dom';

const Sidebar = () =>  {
  const navigate = useNavigate();

  const { token } = useToken();
  var decodedToken = jwt_decode(token);

  const [show, setShow] = useState(false);
  const [userName, setUserName] = useState();

  const handleClose = () => setShow(false);
  const handleShow = () => {
    setShow(true);
  }
  const handleSubmit = async event => {
    event.preventDefault();
    console.log(userName);
    navigate('/fetch', { state: { q: userName } });
    handleClose();
  };
  return (
    <>
    <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
      <Container>
        <Navbar.Brand href="/">FakeBank</Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/statements"><FontAwesomeIcon icon={faHistory} /> Transactions</Nav.Link>
            <NavDropdown title="Account" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/accountDetails">
                <FontAwesomeIcon icon={faBook} /> View Accounts
              </NavDropdown.Item>
              <NavDropdown.Item href="/createAccount">
                <FontAwesomeIcon icon={faShield} /> Create New Account
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item href="/">
                <FontAwesomeIcon icon={faRectangleXmark} /> Close Account
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
          <Nav>            
            <NavDropdown title="admin" id="collasible-nav-dropdown">
              <NavDropdown.Item onClick={handleShow}>
                <FontAwesomeIcon icon={faSearch} /> Search Account
              </NavDropdown.Item>              
            </NavDropdown>
          </Nav>
          <Nav>            
            <NavDropdown title={decodedToken.preferred_username} id="collasible-nav-dropdown">
              <NavDropdown.Item href="/">
                <FontAwesomeIcon icon={faUser} /> Logout
              </NavDropdown.Item>              
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Search Account by Username</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Row>
              <Col xs={6}>
                  <Form.Group className="mb-3" controlId="formBasicUsername">
                      <Form.Label>Username</Form.Label>
                      <Form.Control type="text" placeholder="UserName" onChange={e => setUserName(e.target.value)} />
                  </Form.Group>
              </Col>
              <Col xs={6}>
              </Col>
          </Row>
          <Row>
              <Col xs={12}>
                  <Button variant="primary" type="submit">
                      Submit
                  </Button>
              </Col>
          </Row>
        </Form>        
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
        <Button variant="primary" onClick={handleClose}>
          Save Changes
        </Button>
      </Modal.Footer>
    </Modal>
    </>
  );
};

export default Sidebar;