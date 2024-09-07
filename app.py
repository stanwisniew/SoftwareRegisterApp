from flask import Flask, render_template, jsonify

app = Flask(__name__)

SOFTWARE = [
{
        'id': 1,
        'title': 'Autocad 2024',
        'licensing': 'Very expensive',
        'approved': 'CAD teams'
    },
    {
        'id': 2,
        'title': 'Adobe Photoshop CC',
        'licensing': 'Subscription-based',
        'approved': 'Design teams'
    },
    {
        'id': 3,
        'title': 'Microsoft Office 2021',
        'licensing': 'One-time purchase',
        'approved': 'All departments'
    },
    {
        'id': 4,
        'title': 'Slack',
        'licensing': 'Freemium with paid options',
        'approved': 'Communications'
    },
    {
        'id': 5,
        'title': 'VMware Workstation Pro',
        'licensing': 'Perpetual license',
        'approved': 'IT department'
    }
]

@app.route("/")
def hello_world():
    return render_template('index.html', software=SOFTWARE)

@app.route("/info")
def list_software():
    return jsonify(SOFTWARE)

print(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)