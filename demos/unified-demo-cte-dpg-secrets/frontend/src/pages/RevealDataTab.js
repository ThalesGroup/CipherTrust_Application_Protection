import * as React from 'react';
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

const rowsPHI = [
    { id: 1, name: 'John Doe', healthCard: '123456-789-RL', zip: 'K2V0P3', dob: '01/01/2000'},
];

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
  const ownerDataPCI = [
    { id: 1, name: 'Test User', cc: '1234-5678-9012-3456', cvv: 888, expiry: '01/01/2025', zip: 'K2V0P3' },
  ];
  const operatorDataPCI = [
    { id: 1, name: 'Test User', cc: '1234-xxxx-xxxx-xxxx', cvv: 888, expiry: '01/01/2025', zip: 'K2V0P3' },
  ];
  const unauthorizedDataPCI = [
    { id: 1, name: 'Test User', cc: 'asdasjdadsjasydatsdio==', cvv: 888, expiry: '01/01/2025', zip: 'K2V0P3' },
  ];
  const [expanded, setExpanded] = React.useState('panel1');
  const [pciData, setPciData] = React.useState(unauthorizedDataPCI);
  const [userType, setUserType] = React.useState('unauthorized');

  const handleUserChange = (event) => {
    setUserType(event.target.value)
    if (event.target.value === "owner") {
        setPciData(ownerDataPCI)
    } else if (event.target.value === "operator") {
        setPciData(operatorDataPCI)
    } else {
        setPciData(unauthorizedDataPCI)
    }
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
          <RevealHealthDataCard rowsFromParent={rowsPHI} />
        </AccordionDetails>
      </Accordion>      
    </div>
  );
}