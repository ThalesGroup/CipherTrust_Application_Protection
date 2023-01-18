import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios';

export default function handler(
    req: NextApiRequest,
    res: NextApiResponse
    ) {
        process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
        //console.log(req);
        // Get data submitted in request's body.
        const body = req.body;

        const config = {
            headers: { 
                Authorization: `Bearer ${body.jwt}`,
                "Access-Control-Allow-Origin": "*"
            }
        };
        axios.get(body.ip + '/api/v1/vault/keys2/?skip=0&limit=100', config).then(response => {
            res.status(200).json({ 
                data: response.data
            })
        })
  }