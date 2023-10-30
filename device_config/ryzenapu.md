Requires 

`GRUB_CMDLINE_LINUX_DEFAULT="quiet splash amdgpu.sg_display=0"`

The amdgpu.sg part prevent screen flickering in 6.2 kernel.

See: https://gitlab.freedesktop.org/drm/amd/-/issues/2354