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

        let payload = {
            id: body.id,
            plaintext: body.plaintext,
            mode: 'CBC',
            nae_key_version_header: true
        }

        const config = {
            headers: { 
                Authorization: `Bearer ${body.jwt}`,
                "Access-Control-Allow-Origin": "*"
            }
        };
        axios.post(body.ip + '/api/v1/crypto/encrypt', payload, config).then(response => {
            res.status(200).json({ 
                data: response.data
            })
        })
  }