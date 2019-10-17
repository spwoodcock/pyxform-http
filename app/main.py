import logging
from tempfile import TemporaryDirectory
import os.path

from flask import Flask, jsonify, request
from pyxform import xls2xform

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    return "Welcome to the pyxform-http! Make a POST request to '/api/v1/convert' to convert an XLSForm to an ODK XForm."


# To test: curl --request POST --data-binary @<FILE_NAME>.xlsx http://127.0.0.1/api/v1/convert
@app.route("/api/v1/convert", methods=["POST"])
def post():
    with TemporaryDirectory() as temp_dir_name:
        try:
            with open(os.path.join(temp_dir_name, "tmp.xml"), "w+") as xform, open(
                os.path.join(temp_dir_name, "tmp.xlsx"), "wb"
            ) as xlsform:
                xlsform.write(request.get_data())
                convert_status = xls2xform.xls2xform_convert(
                    xlsform_path=str(xlsform.name),
                    xform_path=str(xform.name),
                    validate=True,
                    pretty_print=False,
                )

                if convert_status:
                    logger.warning(convert_status)

                if os.path.isfile(xform.name):
                    return response(
                        status=200, result=xform.read(), warnings=convert_status
                    )
                else:
                    return response(error=convert_status)

        except Exception as e:
            logger.error(e)
            return response(error=str(e))


def response(status=400, result=None, warnings=None, error=None):
    return jsonify(status=status, result=result, warnings=warnings, error=error), status


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=80)