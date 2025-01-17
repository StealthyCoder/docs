.. highlight:: sh

.. _ref-linux-wic-installer:

WIC Image Installer
===================

 .. note::

  Only EFI compatible systems are currently supported by the image
  installer (e.g. intel-corei7-64, generic-arm64).

To generate a WIC based image installer, switch the default ``WKS_FILE:sota``
definition for your target machine to ``image-efi-installer.wks``::

  $ cat meta-subscriber-overrides/conf/machine/include/lmp-factory-custom.inc
  # WIC-based installer for the intel-corei7-64 target
  WKS_FILE:intel-corei7-64:sota = "image-efi-installer.wks.in"

  # WIC-based installer for the generic-arm64 target
  WKS_FILE:generic-arm64:sota = "image-efi-installer.wks.in"

As WIC is only capable of consuming one single WKS file (even if multiple are
defined via WKS_FILES), this will force the build system to only generate
installer images by default.

Remove the custom ``WKS_FILE:sota`` override to restore back to the default
behavior and generate normal bootable WIC images.

Testing WIC Image Installer with Qemu (x86)
-------------------------------------------

It is possible to test the WIC image installer with Qemu, all that is
required is an additional block device with enough disk space for the
LmP rootfs image.

If running Qemu without graphics support, make sure that the default console
is set to ``ttyS0,115200``, which can be done manually in grub (by editing
the boot arguments before booting the ``install`` target) or by removing
``console=tty0`` from the image installer by changing
``lmp-factory-custom.inc``::

  $ cat meta-subscriber-overrides/conf/machine/include/lmp-factory-custom.inc
  APPEND:remove:intel-corei7-64 = "console=tty0"

Create the virtual disk device that will be used as target with ``qemu-img``::

  $ qemu-img create -f raw disk.img 4G

Download ``lmp-factory-image-intel-corei7-64.wic`` and ``ovmf.secboot.qcow2``
from your own Factory CI run, then run Qemu with the following arguments::

  $ qemu-system-x86_64 -device virtio-net-pci,netdev=net0,mac=52:54:00:12:35:02 \
      -netdev user,id=net0,hostfwd=tcp::2222-:22 \
      -object rng-random,filename=/dev/urandom,id=rng0 -device virtio-rng-pci,rng=rng0 \
      -drive if=none,id=hd,file=lmp-factory-image-intel-corei7-64.wic,format=raw \
      -device virtio-scsi-pci,id=scsi -device scsi-hd,drive=hd \
      -drive if=none,id=hd2,file=disk.img,format=raw -device scsi-hd,drive=hd2 \
      -drive if=pflash,format=qcow2,file=ovmf.secboot.qcow2 -no-reboot \
      -nographic -m 1024 -serial mon:stdio -serial null -cpu host -enable-kvm

Now just follow the instructions provided by the installer in order to
install the actual LmP image into ``disk.img``.

After completed, hit enter to stop the current Qemu execution and start it
up again, but using ``disk.img`` as the primary block device::

  $ qemu-system-x86_64 -device virtio-net-pci,netdev=net0,mac=52:54:00:12:35:02 \
      -netdev user,id=net0,hostfwd=tcp::2222-:22 \
      -object rng-random,filename=/dev/urandom,id=rng0 -device virtio-rng-pci,rng=rng0 \
      -drive if=none,id=hd,file=disk.img,format=raw \
      -device virtio-scsi-pci,id=scsi -device scsi-hd,drive=hd \
      -drive if=pflash,format=qcow2,file=ovmf.secboot.qcow2 \
      -nographic -m 1024 -serial mon:stdio -serial null -cpu host -enable-kvm

.. note::
   If running qemu on a macOS (x86) host, replace ``-enable-kvm`` with ``-M accel=hvf``.
