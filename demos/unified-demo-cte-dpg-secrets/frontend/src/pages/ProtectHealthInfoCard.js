import React, {useState} from 'react';
import Grid from '@mui/material/Grid';
import { TextField, Button } from '@mui/material';
import axios from "axios";

export default function ProtectHealthInfoCard() {
  const https = require('https')

  const agent = new https.Agent({
    rejectUnauthorized: false,
  })

  function getUID() {
    return Date.now().toString(36);
  }

  const onFileChange = (event) => {
    setUpload(event.target.files[0]);
  };

  const submitPHIForm = async event => {
    event.preventDefault();
    const formData = new FormData();
    formData.append(
        "file",
        upload,
        upload.name
    );
    formData.append("id", id);

    let host="http://localhost"
    let port="8080"
    if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
        host=process.env.REACT_APP_BACKEND_IP_ADDRESS
        port=process.env.REACT_APP_BACKEND_PORT
    }
    let url_add_json = host+':'+port+'/api/health-info/add';
    let url_upload = host+':'+port+'/api/health-info/upload';

    axios({
        method: "post",
        url: url_add_json, 
        data: {id, name, healthCardNum, dob, zip},
        headers: { "Content-Type": "application/json" },
        httpsAgent: agent,
    })
    .then((response) => {
        axios({
            method: "post",
            url: url_upload, 
            data: formData,
            headers: { "Content-Type": "multipart/form-data" },
            httpsAgent: agent,
        })
        .then((response) => {
            console.log(response);
        });
    });
  };

  const[id, setId] = React.useState(getUID());
  const[name, setName] = React.useState('John Doe')
  const[healthCardNum, setHealthCardNum] = React.useState('123456-789-RL')
  const[dob, setDob] = React.useState('01/01/2000')
  const[zip, setZip] = React.useState('A1A1A1')
  const[upload, setUpload] = useState('');

  return (
    <form>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-id"
                    label="ID"
                    disabled
                    defaultValue={id}
                    onChange={e => setId(e.target.value)}
                    fullWidth
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-fullname"
                    label="Patient Name"
                    defaultValue={name}
                    onChange={e => setName(e.target.value)}
                    fullWidth
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-dob"
                    label="Date of Birth"
                    defaultValue={dob}
                    onChange={e => setDob(e.target.value)}
                    fullWidth
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-health-card-name"
                    label="Health Card Name"
                    defaultValue={healthCardNum}
                    onChange={e => setHealthCardNum(e.target.value)}
                    fullWidth
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-zip"
                    label="Zip Code"
                    defaultValue={zip}
                    onChange={e => setZip(e.target.value)}
                    fullWidth
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    id="phi-upload"
                    variant="outlined"
                    type="file"
                    inputProps={{
                        multiple: true
                    }}
                    onChange={e => onFileChange(e)}
                    fullWidth
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid>
            <Button variant="contained" disableElevation onClick={submitPHIForm}>
                Save Health Data
            </Button>
        </Grid>                                
    </form>
  );
}