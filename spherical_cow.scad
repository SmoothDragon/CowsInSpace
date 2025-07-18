$fn=64;
union() {
  translate(v = [0, 30, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("1", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
  translate(v = [40, 0, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("2", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
  translate(v = [-40, 30, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("3", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
  translate(v = [0, 0, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("4", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
  translate(v = [40, 30, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("5", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
  translate(v = [-40, 0, 0]) {
    difference() {
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
          union() {
            sphere(r = 6);
            union() {
              translate(v = [3, 3, 5.3999996]) {
                rotate([0, 100, 0]) {
                  intersection() {
                    sphere(r = 1.5);
                    translate(v = [0, 0, 24]) {
                      translate(v = [-24, -24, -24]) {
                        cube(size = 48);
                      }
                    }
                  }
                }
              }
              mirror(v = [1, 0, 0]) {
                translate(v = [3, 3, 5.3999996]) {
                  rotate([0, 100, 0]) {
                    intersection() {
                      sphere(r = 1.5);
                      translate(v = [0, 0, 24]) {
                        translate(v = [-24, -24, -24]) {
                          cube(size = 48);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      translate(v = [0, 0, 18]) {
        linear_extrude(height = 5, twist = 0, slices = 0, center = false) {
          text("6", font="B612 Mono", halign="center", valign="center");
        }
      }
    }
  }
}
