<!DOCTYPE html>
<html lang="en">

<head>
  <title>Bootstrap Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.datatables.net/1.10.24/css/jquery.dataTables.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
  <script>
    $(document).ready(function () {
      $('#statsTable').DataTable({
        "pageLength": 50
      });
    });
  </script>
  <style>
    .table-container {
      max-height: 550px; /* Adjust the height as needed */
      overflow-y: auto; /* Enable vertical scrolling */
      border: 1px solid #ddd; /* Add a border around the table */
      border-radius: 4px; /* Rounded corners */
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th,
    td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: center;
    }

    th {
      background-color: #f2f2f2;
    }

    tr:nth-child(even) {
      background-color: #f2f2f2;
    }

    tr:hover {
      background-color: #ddd;
    }
  </style>
</head>

<body>
  <div class="container-fluid">
    <div class="panel panel-default">
      <div class="panel-heading">
          Matches Statistics
      </div>
      <div class="panel-body col-md-8">
        <div class="table-container">
          <table id="statsTable" class="table table-striped">
            <thead>
              <tr>
                <th>Name</th>
                <th>Batting_First</th>
                <th>Bowling_First</th>
                <th>Batting_Second</th>
                <th>Bowling_Second</th>
              </tr>
            </thead>
            <tbody>
              {% for x in stats %}
              <tr>
                <td>{{ x.player_name }}</td>
                <td><a href="{{ x.Batting_First }}" target="_blank">T20_Batting_First</a></td>
                <td><a href="{{ x.Bowling_First }}" target="_blank">T20_Bowling_First</a></td>
                <td><a href="{{ x.Batting_Second }}" target="_blank">T20_Batting_Second</a></td>
                <td><a href="{{ x.Bowling_Second }}" target="_blank">T20_Bowling_Second</a></td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
