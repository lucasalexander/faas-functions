# pdf_fill
This is an OpenFaaS function that uses Python and [PDFtk](https://www.pdflabs.com/tools/pdftk-server/) to complete PDF forms with client-provided inputs.

The client must supply a base64-encoded copy of the form or a URL from where the form can be downloaded. The values to set in the form are specified in an array of name-value pairs, where the names are the underlying PDF form field names. The completed PDF form is then returned to the client as either a base64-encoded string in a JSON object or as an actual PDF file. Additionally the client can specify whether the form should be flattened to prevent further updates to the form fields.


The sample request below will retrieve a form from a remote server and return the response in base64.
```
{
"action":"render", //render or dumpfields
"flatten":"false", //true or false
"output":"b64", //b64 or pdf
"fields":[{"name":"Text1.1","value":"XXXXX1234"},{"name":"Text1.2","value":"LucasCo"},{"name":"Text1.3","value":"987-XXX"}],
"pdfurl":"https://dor.georgia.gov/sites/dor.georgia.gov/files/related_files/document/MVD/Form/MV_Tag_and_or_Title_Application_Form_MV1_0.pdf"
}
```

The response would look like this.
```
{"pdfdata": "JVBERi0xLjYKJeLjz9MKMSAw........"}
```

Alternatively the client could request the response as a PDF like this:
```
{
"action":"render", //render or dumpfields
"flatten":"false", //true or false
"output":"pdf", //b64 or pdf
"fields":[{"name":"Text1.1","value":"XXXXX1234"},{"name":"Text1.2","value":"LucasCo"},{"name":"Text1.3","value":"987-XXX"}],
"pdfurl":"https://dor.georgia.gov/sites/dor.georgia.gov/files/related_files/document/MVD/Form/MV_Tag_and_or_Title_Application_Form_MV1_0.pdf"
}
```

The client can supply the form as part of the request by supplying a base64-encoded "pdfdata" value instead of a "pdfurl" value.
```
{
"action":"render",
"flatten":"false",
"output":"pdf",
"fields":[{"name":"FillText1","value":"XXXXX1234"},{"name":"FillText2","value":"LucasCo"},{"name":"FillText2","value":"987-XXX"}],
"pdfdata":"JVBERi0xLjYKJeLjz9MKMSAw........"
}
```

In order to determine the available field names and data types, the function also has a "dumpfields" action that will inspect the PDF and return a list of all fields, types and possible values (for combo boxes) as a plain text string.

```
{
"action":"dumpfields",
"pdfurl":"https://dor.georgia.gov/sites/dor.georgia.gov/files/related_files/document/MVD/Form/MV_Tag_and_or_Title_Application_Form_MV1_0.pdf"
}
```

This will return output like the following:
```
---
FieldType: Text
FieldName: Text1.1
FieldFlags: 12582912
FieldJustification: Left
---
FieldType: Text
FieldName: Text1.2
FieldFlags: 12582912
FieldJustification: Left
---
FieldType: Text
FieldName: Text1.3
FieldFlags: 12582912
FieldJustification: Left
FieldMaxLength: 5
---
FieldType: Text
FieldName: Text1.4
FieldFlags: 12582912
FieldJustification: Left
FieldMaxLength: 5
---

...

...

...
```

**Caveats**
1. The form must not be encrypted or password protected. In general, if you can download the form from the internet and complete it using something like Adobe Acrobat Reader without needing to supply a password, this should work.
2. When retrieving the form from remote addresses, TLS/SSL certificates are not validated for HTTPS hosts. This should be not be a security issue as the function does not submit any sensitive data.
3. This function will only work with fillable PDF forms generated with Adobe Acrobat Pro (or something similar). XFA forms generated with Adobe LiveCycle will not work. 