import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Breadcrumb } from '@themesberg/react-bootstrap';
import { faHome, faAngleDown, faAngleUp } from '@fortawesome/free-solid-svg-icons';
import { faGoogle, faTwitter, faYahoo, faYoutube } from '@fortawesome/free-brands-svg-icons';
import { faGlobeEurope, } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, ProgressBar } from '@themesberg/react-bootstrap';

const BootstrapTables = () => {
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
    const { id, source, sourceIcon, sourceIconColor, sourceType, category, rank, trafficShare, change } = props;

    return (
      <tr>
        <td>
          <Card.Link href="#" className="text-primary fw-bold">{id}</Card.Link>
        </td>
        <td className="fw-bold">
          <FontAwesomeIcon icon={sourceIcon} className={`icon icon-xs text-${sourceIconColor} w-30`} />
          {source}
        </td>
        <td>{sourceType}</td>
        <td>{category ? category : "--"}</td>
        <td>{rank ? rank : "--"}</td>
        <td>
          <Row className="d-flex align-items-center">
            <Col xs={12} xl={2} className="px-0">
              <small className="fw-bold">{trafficShare}%</small>
            </Col>
            <Col xs={12} xl={10} className="px-0 px-xl-1">
              <ProgressBar variant="primary" className="progress-lg mb-0" now={trafficShare} min={0} max={100} />
            </Col>
          </Row>
        </td>
        <td>
          <ValueChange value={change} suffix="%" />
        </td>
      </tr>
    );
  };

  const pageTraffic = [
    { id: 1, source: "Direct", sourceType: "Direct", trafficShare: 51, change: 2.45, sourceIcon: faGlobeEurope, sourceIconColor: "gray" },
    { id: 2, source: "Google Search", sourceType: "Search / Organic", trafficShare: 18, change: 17.67, sourceIcon: faGoogle, sourceIconColor: "info" },
    { id: 3, source: "youtube.com", sourceType: "Social", category: "Arts and Entertainment", rank: 2, trafficShare: 27, sourceIcon: faYoutube, sourceIconColor: "danger" },
    { id: 4, source: "yahoo.com", sourceType: "Referral", category: "News and Media", rank: 11, trafficShare: 8, change: -9.30, sourceIcon: faYahoo, sourceIconColor: "purple" },
    { id: 5, source: "twitter.com", sourceType: "Social", category: "Social Networks", rank: 4, trafficShare: 4, sourceIcon: faTwitter, sourceIconColor: "info" }
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
                <th className="border-0">Traffic Source</th>
                <th className="border-0">Source Type</th>
                <th className="border-0">Category</th>
                <th className="border-0">Global Rank</th>
                <th className="border-0">Traffic Share</th>
                <th className="border-0">Change</th>
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

export default BootstrapTables;