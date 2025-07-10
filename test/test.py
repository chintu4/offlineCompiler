import unittest
from main import CodeCompiler

class Test(unittest.TestCase):
    def setUp(self):
        self.tc=CodeCompiler()
    def test_rust(self):
        case1="""
        fn main(){
            println!("hello");
            }
        """
        case2="""
        use rand::Rng;
        
        fn main(){
           let mut rng=rand::thread_rng();
           let num:u32=rng.gen_range(1..=100);
           println!("Random number: {}",num);
         }
        """
        case3="""
use eframe::egui;

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "Hello egui",
        options,
        Box::new(|_cc| Box::new(MyApp::default())),
    )
}

#[derive(Default)]
struct MyApp {
    counter: i32,
}

impl eframe::App for MyApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Welcome to egui!");
            if ui.button("Click me").clicked() {
                self.counter += 1;
            }
            ui.label(format!("Clicked {} times", self.counter));
        });
    }
}

        
        """
        case=[case3]
        for i in case:
            out=self.tc.compile_and_execute(code=i,
                user_input='',
                language='rust',
                compiler_options='',
            
            )
            print(out)

if __name__=='__main__':
    unittest.main()