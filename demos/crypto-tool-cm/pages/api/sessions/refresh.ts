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
            grant_type: "refresh_token",
            refresh_token: body.refresh_token
        }
        axios.post(body.ip + '/api/v1/auth/tokens', payload).then(response => {
            console.log("anurag" + response)
            res.status(200).json({ 
                name: body.name,
                ip: body.ip,
                jwt: response.data.jwt,
                refresh_token: body.refresh_token
            })
        })
  }