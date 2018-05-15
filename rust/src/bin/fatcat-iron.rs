#![allow(missing_docs)]

extern crate chrono;
extern crate clap;
extern crate fatcat;
extern crate fatcat_api;
extern crate futures;
extern crate iron;
extern crate iron_slog;
extern crate swagger;
#[macro_use] extern crate error_chain;
#[macro_use] extern crate slog;
extern crate slog_term;
extern crate slog_async;

use slog::{Drain, Logger};
use iron_slog::{LoggerMiddleware, DefaultLogFormatter};
use clap::{App, Arg};
use iron::{Chain, Iron};
use swagger::auth::AllowAllMiddleware;

/// Create custom server, wire it to the autogenerated router,
/// and pass it to the web server.
fn main() {
    let matches = App::new("server")
        .arg(
            Arg::with_name("https")
                .long("https")
                .help("Whether to use HTTPS or not"),
        )
        .get_matches();


    let decorator = slog_term::TermDecorator::new().build();
    let drain = slog_term::CompactFormat::new(decorator).build().fuse();
    let drain = slog_async::Async::new(drain).build().fuse();
    let logger = Logger::root(drain, o!());
    let formatter = DefaultLogFormatter;

    dotenv().ok();
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    let diesel_middleware: DieselMiddleware<diesel::pg::PgConnection> = DieselMiddleware::new(database_url).unwrap();

    let server = fatcat::server().unwrap();
    let router = fatcat_api::router(server);

    let mut chain = Chain::new(
        LoggerMiddleware::new(router, logger, formatter ));

    chain.link_before(fatcat_api::server::ExtractAuthData);
    // add authentication middlewares into the chain here
    // for the purpose of this example, pretend we have authenticated a user
    chain.link_before(AllowAllMiddleware::new("cosmo"));

    chain.link_after(fatcat::XClacksOverheadMiddleware);
    chain.link_before(diesel_middleware);

    if matches.is_present("https") {
        unimplemented!()
    } else {
        // Using HTTP
        Iron::new(chain)
            .http("localhost:8080")
            .expect("Failed to start HTTP server");
    }
}
