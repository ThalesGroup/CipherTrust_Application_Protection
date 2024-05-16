
import React from "react";
import { Col, Row, Button, Container, InputGroup } from '@themesberg/react-bootstrap';
import { Link } from 'react-router-dom';
import { Routes } from "../../routes";
import BgImage from "../../assets/img/illustrations/signin.svg";
import {useKindeAuth} from "@kinde-oss/kinde-auth-react";

export default () => {
  const { login, register } = useKindeAuth();
  const { user, isAuthenticated, isLoading, getPermission, getPermissions } = useKindeAuth();
  return (
    <main>
      <section className="d-flex align-items-center my-5 mt-lg-6 mb-lg-5">
        <Container>
          <Row className="justify-content-center form-bg-image" style={{ backgroundImage: `url(${BgImage})` }}>
            <Col xs={12} className="d-flex align-items-center justify-content-center">
              <div className="bg-white shadow-soft border rounded border-light p-4 p-lg-5 w-100 fmxw-500">
                <div className="text-center text-md-center mb-4 mt-md-0">
                  <h3 className="mb-0">Please Login or Register</h3>
                  <div className="mt-3 mb-4 text-center">
                    <span className="fw-normal">---</span>
                  </div>
                  <Button variant="primary" onClick={login} className="w-100">
                    Log In
                  </Button>
                  <div className="mt-3 mb-4 text-center">
                    <span className="fw-normal">or</span>
                  </div>
                  <Button onClick={register} className="w-100">
                    Register
                  </Button>
                  <div className="mt-3 mb-4 text-center">
                    <span className="fw-normal">Authentication powered by kinde</span>
                  </div>
                </div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </main>
  );
};
