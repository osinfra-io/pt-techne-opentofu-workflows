run "default" {
  command = apply
}

run "intentional_failure" {
  command = plan

  assert {
    condition     = 1 == 2
    error_message = "Intentional failure for testing job summaries."
  }
}
