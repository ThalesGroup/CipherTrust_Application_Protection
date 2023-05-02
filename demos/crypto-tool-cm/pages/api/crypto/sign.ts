import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios';

export default function handler(
    req: NextApiRequest,
    res: NextApiResponse
    ) {
        process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
        // Get data submitted in request's body.
        const body = req.body;

        const config = {
            headers: { 
                Authorization: `Bearer ${body.jwt}`,
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/octet-stream'
            }
        };

        axios.post(body.ip + '/api/v1/crypto/sign?keyName='+body.keyName+'&signAlgo='+body.signAlgo+'&hashAlgo='+body.hashAlgo, 
            Buffer.from(body.unsignedData), 
            config).then(response => {
                res.status(200).json({ 
                    data: response.data
                })
            })
  }