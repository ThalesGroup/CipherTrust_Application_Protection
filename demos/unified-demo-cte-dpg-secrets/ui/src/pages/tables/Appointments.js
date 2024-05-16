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

const Appointments = () => {
  let host="localhost"
  let port="8080"
  if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
      host=process.env.REACT_APP_BACKEND_IP_ADDRESS
      port=process.env.REACT_APP_BACKEND_PORT
  }
  const [reports, setReports] = useState("");
  const { user, isAuthenticated, isLoading, getPermission, getPermissions, getToken } = useKindeAuth();

  useEffect(() => {
    let accessToken = sessionStorage.getItem('__T__');
    let url = 'http://'+host+':'+port+'/api/lab-requests'
    axios
        .get(url, { headers: {"Authorization" : `Bearer ${accessToken}`} })
        .then((res) => {
          setReports(res.data);
        })
        .catch((err) => console.log(err));
  }, []);

  const rows = {};
  for (const report of reports) {
    if (report.id in rows) {
      rows[report.id].push(report);
    } else {
      rows[report.id] = [report];
   }
  }

  return (
    <>
      <div className="d-xl-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-xl-0">
          <Breadcrumb className="d-none d-md-inline-block" listProps={{ className: "breadcrumb-dark breadcrumb-transparent" }}>
            <Breadcrumb.Item><FontAwesomeIcon icon={faHome} /></Breadcrumb.Item>
            <Breadcrumb.Item>Records</Breadcrumb.Item>
            <Breadcrumb.Item active>Lab Results</Breadcrumb.Item>
          </Breadcrumb>
          <h4>Lab Results</h4>
          <p className="mb-0">
            View patients' lab results
          </p>
        </div>
      </div>

      <Card border="light" className="shadow-sm mb-4">
        <Card.Body className="pb-0">
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
                Object.entries(rows).map((entry) => {
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
    </>
  );
};

export default Appointments;