import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Breadcrumb } from '@themesberg/react-bootstrap';
import { faHome, faAngleDown, faAngleUp, faDownload } from '@fortawesome/free-solid-svg-icons';
import { faGoogle, faTwitter, faYahoo, faYoutube } from '@fortawesome/free-brands-svg-icons';
import { faGlobeEurope, } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, ProgressBar } from '@themesberg/react-bootstrap';

const TestReports = () => {
  const ValueChange = ({ value, suffix }) => {
    const valueIcon = value < 0 ? faAngleDown : faAngleUp;
    const valueTxtColor = value < 0 ? "text-danger" : "text-success";
  
    return (
      value ? <span className={valueTxtColor}>
        <FontAwesomeIcon icon={valueIcon} />
        <span className="fw-bold ms-1">
          {Math.abs(value)}{suffix}
        </span>
      </span> : "--"
    );
  };

  const TableRow = (props) => {
    const { id, name, dateRequisition, action } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td className="fw-bold">
          {name}
        </td>
        <td>{dateRequisition}</td>
        <td>
            <FontAwesomeIcon icon={faDownload} />
        </td>
      </tr>
    );
  };

  const pageTraffic = [
    { id: 1, name: "Jane Doe", dateRequisition: "03/01/2024", action: faGlobeEurope },
    { id: 2, name: "John Doe", dateRequisition: "03/10/2024", action: faGlobeEurope },
  ];
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
                <th className="border-0">#</th>
                <th className="border-0">Patient Name</th>
                <th className="border-0">Requisition Date</th>
                <th className="border-0">Action</th>
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

export default TestReports;