import React, {useEffect, useState} from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Breadcrumb } from '@themesberg/react-bootstrap';
import { faHome, faAngleDown, faAngleUp, faTrash, faDownload, faExpand, faPlus, faBoxOpen, faExpandArrowsAlt, faExpandAlt } from '@fortawesome/free-solid-svg-icons';
import { faGoogle, faTwitter, faYahoo, faYoutube } from '@fortawesome/free-brands-svg-icons';
import { faGlobeEurope, } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, ProgressBar } from '@themesberg/react-bootstrap';
import { Link } from "react-router-dom";
import axios from 'axios';
import { useKindeAuth } from "@kinde-oss/kinde-auth-react";

const PatientRecords = () => {
  const [patients, setPatients] = useState("");
  const { user, isAuthenticated, isLoading, getPermission, getPermissions, getToken } = useKindeAuth();

  useEffect(() => {
    let accessToken = sessionStorage.getItem('__T__');
    let host="localhost"
    let port="8080"
    if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
        host=process.env.REACT_APP_BACKEND_IP_ADDRESS
        port=process.env.REACT_APP_BACKEND_PORT
    }

    let url = 'http://'+host+':'+port+'/api/patients'
    axios
        .get(url, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
            setPatients(res.data);
        })
        .catch((err) => console.log(err));
  }, []);

  const rows = {};
  for (const patient of patients) {
    if (patient.id in rows) {
      rows[patient.id].push(patient);
    } else {
      rows[patient.id] = [patient];
   }
  }

  return (
    <>
      <div className="d-xl-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-xl-0">
          <Breadcrumb className="d-none d-md-inline-block" listProps={{ className: "breadcrumb-dark breadcrumb-transparent" }}>
            <Breadcrumb.Item><FontAwesomeIcon icon={faHome} /></Breadcrumb.Item>
            <Breadcrumb.Item>Records</Breadcrumb.Item>
            <Breadcrumb.Item active>Patients</Breadcrumb.Item>
          </Breadcrumb>
          <h4>Patient Records</h4>
          <p className="mb-0">
            View patient records and associated reports
          </p>
        </div>
      </div>

      <Card border="light" className="shadow-sm mb-4">
        <Card.Body className="pb-0">
          <Table responsive className="table-centered table-nowrap rounded mb-0">
            <thead className="thead-light">
              <tr>
                <th className="border-0">#</th>
                <th className="border-0">Patient Name</th>
                <th className="border-0">Date of Birth</th>
                <th className="border-0">City of Residence</th>
                <th className="border-0">Contact Number</th>
                <th className="border-0">Email</th>
                <th className="border-0">Actions</th>
              </tr>
            </thead>
            <tbody>
              {
                Object.entries(rows).map((entry) => {
                  const row = entry[0];
                  const details = entry[1];
                  return(
                    <tr key={`patient-${row}`}>
                      <td><Card.Link href="#" className="text-primary fw-bold">
                        <Link to={{ pathname: '/patient/details', state: {uid: details[0].id}}}><FontAwesomeIcon icon={faExpandAlt} /></Link>
                      </Card.Link></td>
                      <td className="fw-bold">
                        <Link to={{ pathname: '/patient/details', state: {uid: details[0].id}}}>{details[0].firstName} {details[0].lastName}</Link>
                      </td>
                      <td>{details[0].dateOfBirth}</td>
                      <td>{details[0].city}</td>
                      <td>{details[0].contactNumber}</td>
                      <td>{details[0].email}</td>
                      <td><FontAwesomeIcon icon={faTrash} /> // <FontAwesomeIcon icon={faDownload} /></td>
                    </tr>
                  )
                })}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </>
  );
};

export default PatientRecords;