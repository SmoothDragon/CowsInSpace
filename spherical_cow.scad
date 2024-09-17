$fn=64;
union() {
  intersection() {
    translate(v = [0, 0, 8.485281]) {
      sphere(r = 12);
    }
    translate(v = [0, 0, 24]) {
      translate(v = [-24, -24, -24]) {
        cube(size = 48);
      }
    }
  }
  intersection() {
    union() {
      hull() {
        translate(v = [5.1000004, 8.83346, 7.2124896]) {
          sphere(r = 3);
        }
        translate(v = [0, 0, -12]) {
          translate(v = [5.1000004, 8.83346, 7.2124896]) {
            sphere(r = 3);
          }
        }
      }
      mirror(v = [1, 0, 0]) {
        hull() {
          translate(v = [5.1000004, 8.83346, 7.2124896]) {
            sphere(r = 3);
          }
          translate(v = [0, 0, -12]) {
            translate(v = [5.1000004, 8.83346, 7.2124896]) {
              sphere(r = 3);
            }
          }
        }
      }
      mirror(v = [0, 1, 0]) {
        union() {
          hull() {
            translate(v = [5.1000004, 8.83346, 7.2124896]) {
              sphere(r = 3);
            }
            translate(v = [0, 0, -12]) {
              translate(v = [5.1000004, 8.83346, 7.2124896]) {
                sphere(r = 3);
              }
            }
          }
          mirror(v = [1, 0, 0]) {
            hull() {
              translate(v = [5.1000004, 8.83346, 7.2124896]) {
                sphere(r = 3);
              }
              translate(v = [0, 0, -12]) {
                translate(v = [5.1000004, 8.83346, 7.2124896]) {
                  sphere(r = 3);
                }
              }
            }
          }
        }
      }
    }
    translate(v = [0, 0, 24]) {
      translate(v = [-24, -24, -24]) {
        cube(size = 48);
      }
    }
  }
  translate(v = [0, 9.6, 9]) {
    sphere(r = 6);
  }
}
