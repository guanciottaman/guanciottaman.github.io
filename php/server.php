<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
  $name = $_POST["name"];
  $email = $_POST["email"];
  $message = $_POST["message"];

  $to = "italia.matteo00@gmail.com"; // Replace with the recipient's email address
  $subject = "New Contact Form Submission";
  $headers = "From: $email";

  if (mail($to, $subject, $message, $headers)) {
    $response = array("success" => true);
  } else {
    $response = array("success" => false);
  }

  echo json_encode($response);
}
?>
