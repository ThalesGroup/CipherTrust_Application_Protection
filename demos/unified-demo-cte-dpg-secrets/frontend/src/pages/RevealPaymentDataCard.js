import * as React from 'react';
import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
    { field: 'id', headerName: 'ID', width: 100 },
    { field: 'name', headerName: 'Name', width: 200, editable: false},
    { field: 'cc', headerName: 'Credit Card', width: 220, editable: false },
    { field: 'cvv', headerName: 'CVV', type: 'number', width: 100, editable: false },
    { field: 'expiry', headerName: 'Expiry Date', width: 120, editable: false },
    { field: 'zip', headerName: 'Zip Code', width: 100, editable: false },
];

export default function RevealPaymentDataCard({rowsFromParent}) {
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