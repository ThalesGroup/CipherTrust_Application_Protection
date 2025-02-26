import * as React from 'react';
import PropTypes from 'prop-types';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import ProtectDataTab from './ProtectDataTab';
import RevealDataTab from './RevealDataTab';

function MainTabPane(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

MainTabPane.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

export default function BasicTabs() {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Protect Data" {...a11yProps(0)} />
          <Tab label="Reveal Data" {...a11yProps(1)} />
          <Tab label="Notes" {...a11yProps(2)} />
        </Tabs>
      </Box>
      <MainTabPane value={value} index={0}>
        <ProtectDataTab />
      </MainTabPane>
      <MainTabPane value={value} index={1}>
        <RevealDataTab />
      </MainTabPane>
      <MainTabPane value={value} index={2}>
        Item Three
      </MainTabPane>
    </Box>
  );
}