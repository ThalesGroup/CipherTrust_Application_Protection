import * as React from 'react';
import Grid from '@mui/material/Grid';
import { TextField, Button } from '@mui/material';

export default function ProtectHealthInfoCard() {
  const[name, setName] = React.useState('John Doe')
  const[healthCardNum, setHealthCardNum] = React.useState('123456-789-RL')
  const[dob, setDob] = React.useState('01/01/2000')
  const[zip, setZip] = React.useState('A1A1A1')

  async function addPHIData(data) {
    console.log(data)
  }

  const submitPHIForm = async event => {
    event.preventDefault();    
    await addPHIData({
      name,
      healthCardNum,
      zip,
      dob
    });
  };

  return (
    <form>
        <Grid container spacing={5}>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-fullname"
                    label="Patient Name"
                    defaultValue={name}
                    onChange={e => setName(e.target.value)}
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-health-card-name"
                    label="Health Card Name"
                    defaultValue={healthCardNum}
                    onChange={e => setHealthCardNum(e.target.value)}
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
                />
            </Grid>
            <Grid item xs={6}>
                <TextField
                    required
                    id="phi-dob"
                    label="Date of Birth"
                    defaultValue={dob}
                    onChange={e => setDob(e.target.value)}
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