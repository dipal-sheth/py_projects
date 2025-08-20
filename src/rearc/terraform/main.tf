provider "aws" {
  region = "us-east-1"
}
# provider.tf file needed

resource "aws_sqs_queue" "s3_event_queue" {
  name = "dipal-sqs-queue"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "dipal-projects-bucket"
  force_destroy = true
}


resource "aws_iam_role" "lambda_exec_role" {
  name = "dipal-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_sqs_permissions" {
  name = "lambda-sqs-access"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      Resource = aws_sqs_queue.s3_event_queue.arn
    }]
  })
}


resource "aws_iam_policy_attachment" "lambda_basic_exec" {
  name       = "dipal-basic-exec"
  roles      = [aws_iam_role.lambda_exec_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "lambda_a" {
  filename         = "${path.module}/lambda_api_2.zip"
  function_name    = "dipal-lambdaA"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda_a.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda_api_2.zip")
  timeout          = 10
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.bucket
    }
  }
}

resource "aws_lambda_function" "lambda_b" {
  filename         = "${path.module}/lambda_processing_3.zip"
  function_name    = "dipal-lambdaB"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda_b.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("${path.module}/lambda_processing_3.zip")
  timeout          = 10
}

resource "aws_lambda_event_source_mapping" "lambda_b_sqs_trigger" {
  event_source_arn = aws_sqs_queue.s3_event_queue.arn
  function_name    = aws_lambda_function.lambda_b.arn
  batch_size       = 1
}

resource "aws_s3_bucket_notification" "s3_to_sqs" {
  bucket = aws_s3_bucket.data_bucket.id

  queue {
    queue_arn = aws_sqs_queue.s3_event_queue.arn
    events    = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_sqs_queue_policy.s3_send_policy]
}

resource "aws_sqs_queue_policy" "s3_send_policy" {
  queue_url = aws_sqs_queue.s3_event_queue.id
  policy    = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "SQS:SendMessage",
        Resource  = aws_sqs_queue.s3_event_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = "arn:aws:s3:::dipal-projects-bucket"
          }
        }
      }
    ]
  })
}
