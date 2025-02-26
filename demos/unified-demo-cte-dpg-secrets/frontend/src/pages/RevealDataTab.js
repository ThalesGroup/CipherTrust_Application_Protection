import React, {useEffect} from 'react';
import axios from 'axios';
import { styled } from '@mui/material/styles';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import RevealHealthDataCard from './RevealHealthDataCard';
import RevealPaymentDataCard from './RevealPaymentDataCard';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

const Accordion = styled((props) => (
  <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
  border: `1px solid ${theme.palette.divider}`,
  '&:not(:last-child)': {
    borderBottom: 0,
  },
  '&::before': {
    display: 'none',
  },
}));

const AccordionSummary = styled((props) => (
  <MuiAccordionSummary
    expandIcon={<ArrowForwardIosSharpIcon sx={{ fontSize: '0.9rem' }} />}
    {...props}
  />
))(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, .05)'
      : 'rgba(0, 0, 0, .03)',
  flexDirection: 'row-reverse',
  '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
    transform: 'rotate(90deg)',
  },
  '& .MuiAccordionSummary-content': {
    marginLeft: theme.spacing(1),
  },
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: '1px solid rgba(0, 0, 0, .125)',
}));

export default function RevealDataTab() {
  const https = require('https')

  const agent = new https.Agent({
    rejectUnauthorized: false,
  })

  let pwdFake = "_F@keP@@S"

  let host="http://localhost"
  let port="8080"
  if (process.env.REACT_APP_BACKEND_IP_ADDRESS !== undefined) {
      host=process.env.REACT_APP_BACKEND_IP_ADDRESS
      port=process.env.REACT_APP_BACKEND_PORT
  }

  const [expanded, setExpanded] = React.useState('panel1');
  const [pciData, setPciData] = React.useState('');
  const [phiData, setPhiData] = React.useState('');
  const [userType, setUserType] = React.useState('unauthorized');

  useEffect(() => {
    let urlPHI = host+':'+port+'/api/health-info'
    let urlPCI = host+':'+port+'/api/payment-info'
    const authHeader = Buffer.from(`${userType}:${pwdFake}`).toString('base64');
    axios
        .get(
          urlPHI, 
          { 
            headers: {"Authorization" : `Basic ${authHeader}`},
            httpsAgent: agent,
          }
        )
        .then((res) => {
          setPhiData(res.data.data);
        })
        .catch((err) => console.log(err));
    axios
        .get(
          urlPCI, 
          { 
            headers: {"Authorization" : `Basic ${authHeader}`},
            httpsAgent: agent,
          }
        )
        .then((res) => {
          setPciData(res.data.data);
        })
        .catch((err) => console.log(err));
    }, [host, port, pwdFake, userType]);

  const handleUserChange = (event) => {
    setUserType(event.target.value)
    let urlPHI = host+':'+port+'/api/health-info'
    let urlPCI = host+':'+port+'/api/payment-info'
    const authHeader = Buffer.from(`${event.target.value}:${pwdFake}`).toString('base64');
    axios
        .get(
          urlPHI, 
          { 
            headers: {"Authorization" : `Basic ${authHeader}`},
            httpsAgent: agent,
          }
        )
        .then((res) => {
          setPhiData(res.data.data);
        })
        .catch((err) => console.log(err));
    axios
        .get(
          urlPCI, 
          { 
            headers: {"Authorization" : `Basic ${authHeader}`},
            httpsAgent: agent,
          }
        )
        .then((res) => {
          setPciData(res.data.data);
        })
        .catch((err) => console.log(err));
  };
  const handleChange = (panel) => (event, newExpanded) => {
    setExpanded(newExpanded ? panel : false);
  };

  return (
    <div>
      <Box sx={{ width: 1/4 }}>
        <FormControl fullWidth>
            <InputLabel id="demo-simple-select-label">Select User</InputLabel>
            <Select
            labelId="demo-simple-select-label"
            id="demo-simple-select"
            value={userType}
            label="Select User"
            onChange={handleUserChange}
            >
            <MenuItem value={"operator"}>operator</MenuItem>
            <MenuItem value={"owner"}>owner</MenuItem>
            <MenuItem value={"unauthorized"}>unauthorized</MenuItem>
            </Select>
        </FormControl>
      </Box>
      <Accordion expanded={expanded === 'panel1'} onChange={handleChange('panel1')}>
        <AccordionSummary aria-controls="panel1d-content" id="panel1d-header">
          <Typography>Payment Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <RevealPaymentDataCard rowsFromParent={pciData} />
        </AccordionDetails>
      </Accordion>
      <Accordion expanded={expanded === 'panel2'} onChange={handleChange('panel2')}>
        <AccordionSummary aria-controls="panel2d-content" id="panel2d-header">
          <Typography>Patient Health Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <RevealHealthDataCard rowsFromParent={phiData} />
        </AccordionDetails>
      </Accordion>      
    </div>
  );
}