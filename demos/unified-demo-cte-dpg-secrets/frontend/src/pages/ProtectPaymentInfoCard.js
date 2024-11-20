import * as React from 'react';
import axios from 'axios';
import Grid from '@mui/material/Grid';
import { TextField, Button } from '@mui/material';

export default function ProtectPaymentInfoCard() {
  const[name, setName] = React.useState('Jane Doe')
  const[cc, setCc] = React.useState('1234-5678-9012-3456')
  const[cvv, setCvv] = React.useState('888')
  const[expiry, setExpiry] = React.useState('01/01/2025')
  const[zip, setZip] = React.useState('A1A1A1')
  const https = require('https')

  const agent = new https.Agent({
    rejectUnauthorized: false,
  })

  async function addPCIData(data) {
    let host="http://localhost"
    let port="8080"
    if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
        host=process.env.REACT_APP_BACKEND_IP_ADDRESS
        port=process.env.REACT_APP_BACKEND_PORT
    }
    let url = host+':'+port+'/api/payment-info'
    axios({
        method: "post",
        url: url,
        data: data,
        headers: { "Content-Type": "application/json" },
        httpsAgent: agent,
    })
    .then((response) => {
        console.log(response);
    });
  }

  const submitPCIForm = async event => {
    event.preventDefault();    
    await addPCIData({
      name,
      cc,
      cvv,
      expiry,
      zip
    });
  };

  return (
    <form>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="pci-fullname"
                    label="Customer Name"
                    defaultValue={name}
                    onChange={e => setName(e.target.value)}
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="pci-ccnum"
                    label="Credit Card Name"
                    defaultValue={cc}
                    onChange={e => setCc(e.target.value)}
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="pci-cvv"
                    label="CVV"
                    defaultValue={cvv}
                    onChange={e => setCvv(e.target.value)}
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="pci-card-exprity"
                    label="Expiry Date"
                    defaultValue={expiry}
                    onChange={e => setExpiry(e.target.value)}
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="pci-zip"
                    label="Zip Code"
                    defaultValue={zip}
                    onChange={e => setZip(e.target.value)}
                />
            </Grid>
        </Grid>
        <Grid>&nbsp;</Grid>
        <Grid>
            <Button variant="contained" disableElevation onClick={submitPCIForm}>
                Save Payment Data
            </Button>
        </Grid>                                
    </form>
  );
}