import React, {Component} from 'react';
import AdminLayout from '../../../layouts/AdminLayout';
import Form from '@rjsf/core';
import validator from "@rjsf/validator-ajv8";
import { ObjectFieldTemplateProps, RJSFSchema, UiSchema, WidgetProps } from "@rjsf/utils";

const schema: RJSFSchema = {
  "title": "Add New Product",
  "type": "object",
  "required": [
    "prodCategory",
    "prodTitle",
    "unitPrice"
  ],
  "properties": {
    "prodCategory": {
      type: "string",
      title: "Select Category",
      enum: ["Women Cloths", "Watches", "Men Cloths", "Accessories"]
    },
    "prodTitle": {
      "type": "string",
      "title": "Title"
    },
    "unitPrice": {
      "type": "string",
      "title": "Unit Price"
    },
    "prodDesc": {
      "type": "string",
      "title": "Description"
    },
    "availableColors": {
      "type": "array",
      "title": "Colors Available",
      "items": {
        "type": "string",
        "enum": [
          "Midnight Black",
          "Smoke Blue",
          "Velvet Red",
          "Candy Cane"
        ]
      },
      "uniqueItems": true
    },
    "availableStyles": {
      "type": "array",
      "title": "Styles Available",
      "items": {
        "type": "string",
        "enum": [
          "Tote",
          "Clutch"
        ]
      },
      "uniqueItems": true
    },
    "prodCode": {
      "type": "string",
      "title": "Product Code"
    },
    "prodDimH": {
      "type": "string",
      "title": "Length (cm)"
    },
    "prodDimD": {
      "type": "string",
      "title": "Length (cm)"
    },
    "prodDimL": {
      "type": "string",
      "title": "Length (cm)"
    },
    "prodComposition": {
      "type": "string",
      "title": "Composition"
    },
    "prodImages": {
      "type": "array",
      "title": "Upload multiple images",
      "items": {
        "type": "string",
        "format": "data-url"
      }
    },
  }
};

const uiSchema: UiSchema = {
  "availableColors": {
    "ui:widget": "checkboxes"
  },
  "availableStyles": {
    "ui:widget": "checkboxes"
  },
  "prodDesc": {
    "ui:widget": "textarea"
  }
}


export default class CreateProduct extends Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit({formData}) {
        console.log(formData);
    }
    
    render() {
        return(
        <AdminLayout>
            <div className='p-5 bg-white'>
                <Form schema={schema} uiSchema={uiSchema} validator={validator} onSubmit={this.handleSubmit}>
                <div className='py-2'>
                  <button className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline' type="submit">Submit</button>
                </div>
                </Form>
            </div>            
        </AdminLayout>
        );
    }
}