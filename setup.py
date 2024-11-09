import setuptools
from setuptools.command.build import build


class BuildPackageProtos(setuptools.Command):
  description = "Command to generate project *_pb2.py modules from .proto files."

  def initialize_options(self):
      pass

  def finalize_options(self):
    pass

  def run(self):
    from grpc_tools import command
    command.build_package_protos(self.distribution.package_dir[''])


class CustomBuild(build):
  sub_commands = [("build_proto_modules", None), *build.sub_commands]


setuptools.setup(
  cmdclass={
    'build_proto_modules': BuildPackageProtos,
    'build': CustomBuild,
  }
)
