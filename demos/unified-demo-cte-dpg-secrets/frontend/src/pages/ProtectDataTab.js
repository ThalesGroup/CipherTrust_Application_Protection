import * as React from 'react';
import { styled } from '@mui/material/styles';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Collapse from '@mui/material/Collapse';
import Avatar from '@mui/material/Avatar';
import IconButton, { IconButtonProps } from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { blue, green } from '@mui/material/colors';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';

import ProtectPaymentInfoCard from './ProtectPaymentInfoCard';
import ProtectHealthInfoCard from './ProtectHealthInfoCard';
import paymentImg from './payment.jpg';
import healthCareImg from './healthcare.jpg';

interface ExpandMoreProps extends IconButtonProps {
  expand: boolean;
}

const ExpandMore = styled((props: ExpandMoreProps) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme, expand }) => ({
  transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),
}));

export default function ProtectDataTab() {
  const [expandedPCI, setExpandedPCI] = React.useState(false);
  const [expandedPHI, setExpandedPHI] = React.useState(false);

  const handleExpandPCIClick = () => {
    setExpandedPCI(!expandedPCI);
  };

  const handleExpandPHIClick = () => {
    setExpandedPHI(!expandedPHI);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={5}>
            <Grid item xs={6}>                
                <Card>
                    <CardHeader
                        avatar={
                        <Avatar sx={{ bgcolor: blue[500] }} aria-label="recipe">
                            PCI
                        </Avatar>
                        }
                        title="Protect Payment Information"
                        subheader="Credit Card and PAN Info"
                    />
                    <CardMedia
                        component="img"
                        height="194"
                        image={paymentImg}
                        alt="Paella dish"
                    />
                    <CardContent>
                        <Typography variant="body2" color="text.secondary">
                        Sample form for storing payment Information in a secured fashion
                        </Typography>
                    </CardContent>
                    <CardActions disableSpacing>
                        <ExpandMore
                            expand={expandedPCI}
                            onClick={handleExpandPCIClick}
                            aria-expanded={expandedPCI}
                            aria-label="show more"
                        >
                            <ExpandMoreIcon />
                        </ExpandMore>
                    </CardActions>
                    <Collapse in={expandedPCI} timeout="auto" unmountOnExit>
                        <CardContent>
                            <ProtectPaymentInfoCard />
                        </CardContent>
                    </Collapse>
                </Card>
            </Grid>
            <Grid item xs={6}>
                <Card>
                    <CardHeader
                        avatar={
                        <Avatar sx={{ bgcolor: green[500] }} aria-label="recipe">
                            PHI
                        </Avatar>
                        }
                        title="Patient Health Information"
                        subheader="health card and other personal info"
                    />
                    <CardMedia
                        component="img"
                        height="194"
                        image={healthCareImg}
                        alt="Paella dish"
                    />
                    <CardContent>
                        <Typography variant="body2" color="text.secondary">
                        Sample form for storing patient confidential information in a secured way
                        </Typography>
                    </CardContent>
                    <CardActions disableSpacing>
                        <ExpandMore
                        expand={expandedPHI}
                        onClick={handleExpandPHIClick}
                        aria-expanded={expandedPHI}
                        aria-label="show more"
                        >
                            <ExpandMoreIcon />
                        </ExpandMore>
                    </CardActions>
                    <Collapse in={expandedPHI} timeout="auto" unmountOnExit>
                        <CardContent>
                            <ProtectHealthInfoCard />
                        </CardContent>
                    </Collapse>
                </Card>
            </Grid>
        </Grid>
    </Box>    
  );
}