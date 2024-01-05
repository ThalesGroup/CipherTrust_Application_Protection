import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Breadcrumb } from '@themesberg/react-bootstrap';
import { faHome, faAngleDown, faAngleUp, faTrash, faDownload } from '@fortawesome/free-solid-svg-icons';
import { faGoogle, faTwitter, faYahoo, faYoutube } from '@fortawesome/free-brands-svg-icons';
import { faGlobeEurope, } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, ProgressBar } from '@themesberg/react-bootstrap';
import { Link } from "react-router-dom";

const PatientRecords = () => {
  const TableRow = (props) => {
    const { id, name, dob, city, contactNum, email, action } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td className="fw-bold">
          <Link to={{ pathname: '/patient/details', state: {uid: id}}}>{name}</Link>
        </td>
        <td>{dob}</td>
        <td>{city}</td>
        <td>{contactNum}</td>
        <td>{email}</td>
        <td>
          <FontAwesomeIcon icon={faTrash} /> // <FontAwesomeIcon icon={faDownload} />
        </td>
      </tr>
    );
  };

  const pageTraffic = [
    { id: 1, name: "Jane Doe", dob: "01/01/2000", city: "Ottawa", contactNum: "+1 234-567-8901", email: "example@ciphertrust.io", action: faGlobeEurope },
    { id: 2, name: "John Doe", dob: "10/10/2000", city: "Toronto", contactNum: "+1 098-765-4321", email: "patient@ciphertrust.io", action: faGlobeEurope },
  ];
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
              {pageTraffic.map(pt => <TableRow key={`page-traffic-${pt.id}`} {...pt} />)}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </>
  );
};

export default PatientRecords;