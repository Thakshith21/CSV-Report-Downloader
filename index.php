<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generate CSV</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7fc;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #333;
        }

        .container {
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
        }

        h1 {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 20px;
        }

        label {
            font-size: 14px;
            color: #555;
            display: block;
            margin-bottom: 8px;
        }

        input[type="date"], input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }

        input[type="text"]:focus, input[type="date"]:focus {
            border-color: #4CAF50;
            outline: none;
        }

        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 16px;
            border-radius: 4px;
            width: 100%;
            cursor: pointer;
            box-sizing: border-box;
        }

        button:hover {
            background-color: #45a049;
        }

        #loading {
            display: none;
            font-weight: bold;
            color: #007bff;
            text-align: center;
            margin-top: 20px;
        }

        #download-link {
            display: none;
            font-weight: bold;
            color: green;
            text-align: center;
            margin-top: 20px;
        }

        .error {
            color: red;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Generate CSV Report</h1>
        <form id="csv-form">
            <label for="start_date">Start Date:</label>
            <input type="date" id="start_date" name="start_date" required><br>

            <label for="end_date">End Date:</label>
            <input type="date" id="end_date" name="end_date" required><br>

            <label for="category">Category:</label>
            <input type="text" id="category" name="category" required><br>

            <button type="submit">Generate Report</button>
        </form>

        <p id="loading">Loading... Please wait.</p>
        <p class="error" id="error-message"></p>
        <a id="download-link" href="#" download>Download CSV</a>
    </div>

    <script>
        $(document).ready(function () {
            $("#csv-form").on("submit", function (e) {
                e.preventDefault(); // Prevent default form submission

                // Get form values
                const startDate = $("#start_date").val();
                const endDate = $("#end_date").val();
                const category = $("#category").val();

                // Validate inputs
                if (!startDate || !endDate || !category) {
                    $("#error-message").text("All fields are required!");
                    return;
                }

                // Ensure start date is not later than end date
                if (new Date(startDate) > new Date(endDate)) {
                    $("#error-message").text("Start Date cannot be later than End Date.");
                    return;
                }

                // Clear any previous error messages
                $("#error-message").text("");

                // Hide the form and show loading message
                $("#csv-form").hide();
                $("#loading").show();
                $("#download-link").hide();  // Hide the download link initially

                // Prepare data to send
                const formData = {
                    start_date: startDate,
                    end_date: endDate,
                    category: category,
                };

                // AJAX request to CGI script
                $.ajax({
                    url: "duplicate.cgi", // Replace with your CGI script URL
                    type: "POST",
                    data: formData,
                    success: function (response) {
                        // Hide loading message
                        $("#loading").hide();

                        // Check if the response contains a valid download link
                        if (response.includes("Download here")) {
                            const link = $(response).find("a").attr("href");
                            $("#download-link").attr("href", link).show(); // Show download link
                        } else {
                            $("#error-message").text(response); // Show error message if no link found
                        }
                    },
                    error: function () {
                        // Hide loading message on error
                        $("#loading").hide();
                        $("#error-message").text("An error occurred while generating the report. Please try again.");
                    }
                });
            });
        });
    </script>
</body>
</html>

