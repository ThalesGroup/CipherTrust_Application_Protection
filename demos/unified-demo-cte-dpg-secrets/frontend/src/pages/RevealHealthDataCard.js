import * as React from 'react';
import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'name', headerName: 'Patient name', width: 150, editable: true },
    { field: 'healthCardNum', headerName: 'Health Card Number', width: 200, editable: true },
    { field: 'zip', headerName: 'Zip Code', type: 'number', width: 110, editable: true },
    { field: 'dob', headerName: 'Date of Birth', width: 110, editable: true },
    { field: 'fileName', headerName: 'Uploaded File', width: 110, editable: true },
];

export default function RevealHealthDataCard({rowsFromParent}) {
    return (
      <Box sx={{ height: 250, width: '100%' }}>
        <DataGrid
          rows={rowsFromParent}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 5,
              },
            },
          }}
          pageSizeOptions={[5]}
          checkboxSelection
          disableRowSelectionOnClick
        />
      </Box>
    );
}