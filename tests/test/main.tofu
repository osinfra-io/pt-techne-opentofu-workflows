# Null Resource
# https://search.opentofu.org/provider/hashicorp/null/latest/docs/resources/resource

resource "null_resource" "hello" {
  provisioner "local-exec" {
    command = "echo 'Hello, World!'"
  }
}
