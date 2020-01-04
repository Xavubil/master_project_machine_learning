using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Rest_Server_ML;

namespace Rest_Server_ML.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class MLController : ControllerBase
    {
        // GET: api/ML
        [HttpGet]
        public IEnumerable<string> Get()
        {
            return new string[] { "value1", "value2" };
        }

        // GET: api/ML/5
        [HttpGet("{id}", Name = "Get")]
        public string Get(int id)
        {
            MLClass.runML();

            return "true";
        }

        // POST: api/ML
        [HttpPost]
        public void Post([FromBody] string value)
        {
        }

        // PUT: api/ML/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody] string value)
        {
        }

        // DELETE: api/ApiWithActions/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {

        }
    }
}
